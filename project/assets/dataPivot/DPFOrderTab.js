import $ from '$';
import _ from 'underscore';
import d3 from 'd3';

import {
    _DataPivot_settings_filters,
    _DataPivot_settings_sorts,
    _DataPivot_settings_spacers,
} from './DataPivotUtilities';
import {
    NULL_CASE,
} from './shared';
import DataPivotVisualization from './DataPivotVisualization';


let build_ordering_tab = function(self){
    var tab = $('<div class="tab-pane" id="data_pivot_settings_ordering">'),
        override_tbody = $('<tbody>'),
        reset_overrides = function(){
            self.settings.row_overrides = [];
            build_manual_rows();
        },
        reset_ordering_overrides = function(){
            self.settings.row_overrides.forEach(function(v){
                v.offset = 0;
            });
        },
        build_manual_rows = function(){
            var rows = [],
                get_selected_fields = function(v){return v.field_name !== NULL_CASE;},
                descriptions = self.settings.description_settings.filter(get_selected_fields),
                filters = self.settings.filters.filter(get_selected_fields),
                sorts = self.settings.sorts.filter(get_selected_fields);

            if(descriptions.length === 0){
                rows.push('<tr><td colspan="6">Please provide description columns before manually filtering.</td></tr>');
                return override_tbody.html(rows);
            }

            // apply filters
            var data_copy = DataPivotVisualization.filter(self.data,
                              filters, self.settings.plot_settings.filter_logic);

            data_copy = _.filter(data_copy,
              _.partial(
                DataPivotVisualization.shouldInclude,
                _,
                self.settings.dataline_settings[0],
                self.settings.datapoint_settings
              )
            );

            if(data_copy.length === 0 ){
                rows.push('<tr><td colspan="6">No rows remaining after filtering criteria.</td></tr>');
                return override_tbody.html(rows);
            }

            // apply sorts
            data_copy = DataPivotVisualization.sorter(data_copy, sorts);

            var row_override_map = d3.map(),
                get_matched_override_or_default = function(pk){
                    var match = row_override_map.get(pk);
                    if(match) return match;
                    return {
                        pk,
                        include: true,
                        offset: 0,
                        text_style: NULL_CASE,
                        line_style: NULL_CASE,
                        symbol_style: NULL_CASE,
                    };
                },
                offsets = [],
                format_offset = function(offset){
                    if(offset>0) return '↓{0}'.printf(offset);
                    if(offset<0) return '↑{0}'.printf(Math.abs(offset));
                    return '';
                };

            self.settings.row_overrides.forEach(function(v){
                row_override_map.set(v.pk, v);
            });

            // build rows
            data_copy.forEach(function(v, i){
                var desc = [],
                    obj = get_matched_override_or_default(v._dp_pk),
                    include = $('<input name="ov_include" type="checkbox">').prop('checked', obj.include),
                    offset_span = $('<span>').text(format_offset(obj.offset)),
                    move_up = $('<button class="btn btn-mini"><i class="icon-arrow-up"></i></button>')
                        .click(function(){
                            var tr = $(this).parent().parent();
                            if (tr.index()>0){
                                var offset = $(this).parent().data('offset')-1;
                                offset_span.text(format_offset(offset));
                                $(this).parent().data('offset', offset);
                                tr.insertBefore(tr.prev())
                                    .animate({'background-color': 'yellow'}, 'fast')
                                    .animate({'background-color': 'none'}, 'slow');
                            }
                        }),
                    move_down = $('<button class="btn btn-mini"><i class="icon-arrow-down"></i></button>')
                        .click(function(){
                            var tr = $(this).parent().parent();
                            if(tr.index()<tr.parent().children().length-1){
                                var offset = $(this).parent().data('offset')+1;
                                offset_span.text(format_offset(offset));
                                $(this).parent().data('offset', offset);
                                tr.insertAfter(tr.next())
                                  .animate({'background-color':'yellow'}, 'fast')
                                  .animate({'background-color':'none'}, 'slow');
                            }
                        }),
                    text_style = self.style_manager.add_select('texts', obj.text_style, true),
                    line_style = self.style_manager.add_select('lines', obj.line_style, true),
                    symbol_style = self.style_manager.add_select('symbols', obj.symbol_style, true);

                descriptions.forEach(function(v2){desc.push(v[v2.field_name]);});
                var tr = $('<tr></tr>').data({pk: v._dp_pk, obj})
                        .append('<td>{0}</td>'.printf(desc.join('<br>')))
                        .append($('<td></td>').append(include))
                        .append($('<td class="ov_offset"></td>').append(offset_span, move_up, move_down).data('offset', obj.offset))
                        .append($('<td class="ov_text"></td>').append(text_style))
                        .append($('<td class="ov_line"></td>').append(line_style))
                        .append($('<td class="ov_symbol"></td>').append(symbol_style));
                rows.push(tr);
                if(obj.offset!==0) offsets.push(obj);
            });

            offsets.forEach(function(os){
                rows.forEach(function(v, i){
                    if ($(v).data('obj') === os){
                        var new_off = i+os.offset;
                        if (new_off >= rows.length) new_off = rows.length-1;
                        if (new_off < 0) new_off = 0;
                        rows.splice(new_off, 0, rows.splice(i, 1)[0]);
                    }
                });
            });

            return override_tbody.html(rows);
        },
        show_rebuild_overrides = function(){
            var btn = $('<button class="btn btn-primary">Click to rebuild</button>')
                        .on('click', build_manual_rows);
            override_tbody.html($('<tr>').append(
                  $('<td colspan="6">Row-ordering has changed.</td>').append('<br>', btn)));
        },
        build_filtering_div = function(){
            var div = $('<div></div>'),
                thead = $('<thead></thead>').html(
                    $('<tr>').append(
                        '<th>Field Name</th>',
                        '<th>Filter Type</th>',
                        '<th>Value</th>',
                        '<th>Ordering</th>')),
                tbody = $('<tbody>'),
                num_rows = (self.settings.filters.length === 0) ? 2 :
                    self.settings.filters.length,
                add_row = function(i){
                    if(!self.settings.filters[i]){
                        self.settings.filters[i] = _DataPivot_settings_filters.defaults();
                    }
                    var obj = new _DataPivot_settings_filters(self, self.settings.filters[i]);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.filters.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
                    .on('click', new_row);

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }

            var filter_logic = function(){
                var lbl = $('<div>'),
                    and = $('<label class="radio inline">AND</label>')
                            .append('<input name="filter_logic" type="radio" value="and">'),
                    or = $('<label class="radio inline">OR</label>')
                            .append('<input name="filter_logic" type="radio" value="or">'),
                    value = self.settings.plot_settings.filter_logic || 'and';

                // set initial value
                if(value==='and'){
                    and.find('input').prop('checked', true);
                } else {
                    or.find('input').prop('checked', true);
                }

                // set event binding to change settings
                self.$settings_div.on('change', 'input[name="filter_logic"]', function(){
                    self.settings.plot_settings.filter_logic = $('input[name="filter_logic"]:checked').val();
                    reset_ordering_overrides();
                    show_rebuild_overrides();
                });

                tbody.on('change autocompletechange', 'input,select', function(){
                    reset_ordering_overrides();
                    show_rebuild_overrides();
                }).on('click', 'button', function(){
                    reset_ordering_overrides();
                    show_rebuild_overrides();
                });

                return lbl.append(
                    '<h4>Filter logic</h4>',
                    '<p class="help-block">Should multiple filter criteria be required for ALL rows (AND), or ANY row (OR)?</p>',
                    and, or);
            }();

            return div.html([
                $('<h3>Row Filters</h3>').append(new_point_button),
                '<p class="help-block">Use filters to determine which components of your dataset should be displayed on the figure.</p>',
                $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody]),
                filter_logic,
            ]);
        },
        build_sorting_div = function(){
            var div = $('<div>'),
                thead = $('<thead>').html([
                   $('<tr>').append('<th>Field Name</th>', '<th>Sort Order</th>', '<th>Ordering</th>'),
                ]),
                tbody = $('<tbody>').on('change', 'input,select', function(){
                    reset_ordering_overrides();
                    show_rebuild_overrides();
                }).on('click', 'button', function(){
                    reset_ordering_overrides();
                    show_rebuild_overrides();
                }),
                num_rows = (self.settings.sorts.length === 0) ? 2 : self.settings.sorts.length,
                add_row = function(i){
                    if(!self.settings.sorts[i]){
                        self.settings.sorts[i] = _DataPivot_settings_sorts.defaults();
                    }
                    var obj = new _DataPivot_settings_sorts(self, self.settings.sorts[i], i);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.sorts.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row);

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }
            return div.html([
                $('<h3>Row Sorting</h3>').append(new_point_button),
                '<p class="help-block">Sorting determines the order which rows will appear; sorts can be overridden using the manual override table below.</p>',
                $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody])]);
        },
        build_spacing_div = function(){
            var div = $('<div>'),
                tbody = $('<tbody>'),
                thead = $('<thead>').html(
                    $('<tr>').append(
                        '<th>Row index</th>',
                        '<th>Show line?</th>',
                        '<th>Line style</th>',
                        '<th>Extra space?</th>',
                        '<th>Delete</th>')),
                num_rows = (self.settings.spacers.length === 0) ? 1 : self.settings.spacers.length,
                add_row = function(i){
                    if(!self.settings.spacers[i]){
                        self.settings.spacers[i] = _DataPivot_settings_spacers.defaults();
                    }
                    var obj = new _DataPivot_settings_spacers(self, self.settings.spacers[i], i);
                    tbody.append(obj.tr);
                },
                new_row = function(){
                    var num_rows = self.settings.spacers.length;
                    add_row(num_rows);
                },
                new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>')
                    .on('click', new_row);

            for(var i=0; i<num_rows; i++){
                add_row(i);
            }
            return div.html([
                $('<h3>Additional Row Spacing</h3>').append(new_point_button),
                '<p class="help-block">Add additional-space between rows, and optionally a horizontal line.</p>',
                $('<table class="table table-condensed table-bordered">')
                    .html([thead, tbody])]);
        },
        build_manual_ordering_div = function(){
            var div = $('<div>'),
                thead = $('<thead>').html(
                    $('<tr>').append(
                        '<th>Description</th>',
                        '<th>Include</th>',
                        '<th>Row Offset</th>',
                        '<th>Override<br>Text Style</th>',
                        '<th>Override<br>Line Style</th>',
                        '<th>Override<br>Symbol Style</th>'));

            return div.html([
                $('<h3>Row-level customization</h3>').append(
                    $('<button class="btn btn-primary pull-right">Reset overrides</button>')
                        .on('click', reset_overrides)),
                $('<p class="help-block">Row-level customization of individual rows after filtering/sorting above. Note that any changes to sorting or filtering will alter these customizations.</p>'),
                $('<table class="table table-condensed table-bordered table-hover tbl_override"></table>').html([thead, override_tbody])]);
        },
        update_override_settings = function(){
            self.settings.row_overrides = [];
            override_tbody.find('tr').each(function(i, v){
                var $v = $(v),
                    obj = {
                        pk: $v.data('pk'),
                        include: $v.find('input[name="ov_include"]').prop('checked'),
                        offset: $v.find('.ov_offset').data('offset'),
                        text_style: $v.find('.ov_text select option:selected').val(),
                        line_style: $v.find('.ov_line select option:selected').val(),
                        symbol_style: $v.find('.ov_symbol select option:selected').val(),
                    };
                // only add if settings are non-default
                if ((obj.include === false) ||
                    (obj.offset !== 0) ||
                    (obj.text_style !== NULL_CASE) ||
                    (obj.line_style !== NULL_CASE) ||
                    (obj.symbol_style !== NULL_CASE)){
                    self.settings.row_overrides.push(obj);
                }
            });
        };

    override_tbody.on('click', 'button', update_override_settings)
        .on('change', 'input,select', update_override_settings);

    // update whenever tab is clicked
    self.$div.on('shown','a.dp_ordering_tab[data-toggle="tab"]', build_manual_rows);

    return tab.html([
        build_filtering_div(), '<hr>',
        build_sorting_div(), '<hr>',
        build_spacing_div(), '<hr>',
        build_manual_ordering_div(),
    ]);
};

export default build_ordering_tab;
