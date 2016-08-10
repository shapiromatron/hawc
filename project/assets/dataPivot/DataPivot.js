import $ from '$';
import _ from 'underscore';
import d3 from 'd3';

import HAWCModal from 'utils/HAWCModal';

import DataPivotDefaultSettings from './DataPivotDefaultSettings';
import DataPivotExtension from './DataPivotExtension';
import DataPivotLegend from './DataPivotLegend';
import {
    _DataPivot_settings_description,
    _DataPivot_settings_linedata,
    _DataPivot_settings_pointdata,
    _DataPivot_settings_filters,
    _DataPivot_settings_sorts,
    _DataPivot_settings_spacers,
    _DataPivot_settings_refline,
    _DataPivot_settings_refrect,
    _DataPivot_settings_label,
    _DataPivot_settings_general,
} from './DataPivotUtilities';
import {
    NULL_CASE,
} from './shared';
import StyleManager from './StyleManager';
import StyleViewer from './StyleViewer';
import DataPivotVisualization from './DataPivotVisualization';


class DataPivot {

    constructor(data, settings, dom_bindings, title, url){
        this.data = data;
        this.settings = settings || DataPivot.default_plot_settings();
        if(dom_bindings.update) this.build_edit_settings(dom_bindings);
        this.title = title;
        this.url = url;
    }

    static get_object(pk, callback){
        $.get('/summary/api/data_pivot/{0}/'.printf(pk), function(d){
            d3.tsv(d.data_url)
              .row(function(d, i){ return DataPivot.massage_row(d, i); })
              .get(function(error, data){
                  var dp = new DataPivot(data,
                      d.settings,
                      {},
                      d.title,
                      d.url);
                  if(callback){callback(dp);} else {return dp;}
              });
        });
    }

    static displayAsModal(id){
        DataPivot.get_object(id, function(d){d.displayAsModal();});
    }

    static displayInline(id, setTitle, setBody){
        DataPivot.get_object(id, (obj)=>{
            var title  = $('<h4>').html(obj.object_hyperlink()),
                content = $('<div>');

            setTitle(title);
            setBody(content);
            obj.build_data_pivot_vis(content);
        });
    }

    static default_plot_settings(){
        return DataPivotDefaultSettings;
    }

    static massage_row(row, i){
        // make numbers in data numeric if possible
        // see https://github.com/mbostock/d3/wiki/CSV
        for(var field in row) {
            if(row.hasOwnProperty(field)){
                row[field] = +row[field] || row[field];
            }
        }

        // add data-pivot row-level key and index
        row._dp_y  = i;
        row._dp_pk = row['key'] || i;

        return row;
    }

    static move_row(arr, obj, moveUp){
      // class-level function; used to delete a settings input row
        var swap = function(arr, a, b){
                if((a<0) || (b<0)) return;
                if((a>=arr.length) || (b>=arr.length)) return;
                arr[a] = arr.splice(b, 1, arr[a])[0];
            },
            idx = arr.indexOf(obj.values);

        if(moveUp){
            obj.tr.insertBefore(obj.tr.prev());
            swap(arr, idx, idx-1);
        } else {
            obj.tr.insertAfter(obj.tr.next());
            swap(arr, idx, idx+1);
        }
    }

    static delete_row(arr, obj){
        // class-level function; used to delete a settings input row
        obj.tr.remove();
        arr.splice(arr.indexOf(obj.values), 1);
    }

    static build_movement_td(arr, self, options){
        //build a td including buttons for movement
        var td = $('<td>'),
            up = $('<button class="btn btn-mini" title="move up"><i class="icon-arrow-up"></button>')
                    .on('click', function(){DataPivot.move_row(arr, self, true);}),
            down = $('<button class="btn btn-mini" title="move down"><i class="icon-arrow-down"></button>')
                    .on('click', function(){DataPivot.move_row(arr, self, false);}),
            del = $('<button class="btn btn-mini" title="remove"><i class="icon-remove"></button>')
                    .on('click', function(){DataPivot.delete_row(arr, self);});

        if(options.showSort) td.append(up, down);
        td.append(del);
        return td;
    }

    static getRowDetails(values){
        var unique = d3.set(values).values(),
            numeric = values.filter(function(v){return $.isNumeric(v); }),
            range = (numeric.length>0) ? d3.extent(numeric) : undefined;

        return {
            unique,
            numeric,
            range,
        };
    }

    static rangeInputDiv(input){
        // given an numeric-range input, return a div containing input and text
        // field which updates based on current value.
        var text = $('<span>').text(input.val());
        input.on('change', function(){text.text(input.val());});
        return $('<div>').append(input, text);
    }

    static displayEditView(data_url, settings, options){
        var dp;

        d3.tsv(data_url)
            .row((d, i) => DataPivot.massage_row(d, i))
            .get((error, data) => {
                $('#loading_div').fadeOut();
                dp = new DataPivot(data, settings,{
                    update: true,
                    container: options.container,
                    data_div: options.dataDiv,
                    settings_div: options.settingsDiv,
                    display_div: options.displayDiv,
                });
            });

        $(options.submissionDiv).submit(function(){
            $(options.settingsField).val(dp.get_settings_json());
            return true;
        });
    }

    build_edit_settings(dom_bindings){
        var self = this,
            editable = true;
        this.style_manager = new StyleManager(this);
        this.$div = $(dom_bindings.container);
        this.$data_div = $(dom_bindings.data_div);
        this.$settings_div = $(dom_bindings.settings_div);
        this.$display_div = $(dom_bindings.display_div);

        // rebuild visualization whenever selected
        $('a[data-toggle="tab"]').on('shown', function(e){
            if (self.$display_div[0] === $($(e.target).attr('href'))[0]){
                self.build_data_pivot_vis(self.$display_div, editable);
            }
        });

        this.build_data_table();
        this.build_settings();
        this.$div.fadeIn();
    }

    build_data_pivot_vis(div, editable){
        delete this.plot;
        editable = editable || false;
        var data = JSON.parse(JSON.stringify(this.data));  // deep-copy
        this.plot = new DataPivotVisualization(data, this.settings, div, editable);
    }

    build_data_table(){
        var tbl = $('<table class="data_pivot_table">'),
            thead = $('<thead>'),
            tbody = $('<tbody>');

        // get headers
        var data_headers = [];
        for(var prop in this.data[0]) {
            if(this.data[0].hasOwnProperty(prop)){
                data_headers.push(prop);
            }
        }

        // print header
        var tr = $('<tr>');
        data_headers.forEach(function(v){
            tr.append('<th>{0}</th>'.printf(v));
        });
        thead.append(tr);

        // print body
        this.data.forEach(function(d){
            var tr = $('<tr>');
            data_headers.forEach(function(field){
                tr.append('<td>{0}</td>'.printf(d[field]));
            });
            tbody.append(tr);
        });

        // insert table
        tbl.append([thead, tbody]);
        this.$data_div.html(tbl);

        // now save things back to object
        this.data_headers = data_headers;
    }

    build_settings(){
        this.dpe_options = DataPivotExtension.get_options(this);
        var self = this,
            build_description_tab = function(){
                var tab = $('<div class="tab-pane active" id="data_pivot_settings_description"></div>'),
                    headers = ['Column header', 'Display name', 'Header style', 'Text style', 'Maximum width (pixels)', 'On-Click'],
                    tbody = $('<tbody></tbody>');

                headers.push('Ordering');

                var thead = $('<thead></thead>').html(headers.map(function(v){return '<th>{0}</th>'.printf(v);}).join('\n')),
                    add_row = function(i){
                        if(!self.settings.description_settings[i]){
                            self.settings.description_settings.push(_DataPivot_settings_description.defaults());
                        }
                        var obj = new _DataPivot_settings_description(self, self.settings.description_settings[i]);
                        tbody.append(obj.tr);
                    },
                    new_row = function(){
                        var num_rows = self.settings.description_settings.length;
                        add_row(num_rows);
                    },
                    new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row),
                    num_rows = (self.settings.description_settings.length === 0) ? 5 : self.settings.description_settings.length;

                for(var i=0; i<num_rows; i++){
                    add_row(i);
                }
                return tab.html([
                    $('<h3>Descriptive Columns</h3>').append(new_point_button),
                    $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody])]);
            },
            build_data_tab = function(){
                var tab = $('<div class="tab-pane" id="data_pivot_settings_data"></div>'),
                    headers = ['Column header', 'Display name', 'Line style'],
                    header_tr = function(lst){
                        var vals = [];
                        lst.forEach(function(v){vals.push('<th>{0}</th>'.printf(v));});
                        return $('<tr></tr>').html(vals);
                    };

                //Build line table
                var thead = $('<thead></thead>').html(header_tr(headers)),
                    tbody = $('<tbody></tbody>');

                if(self.settings.dataline_settings.length === 0){
                    self.settings.dataline_settings.push(_DataPivot_settings_linedata.defaults());
                }

                var obj = new _DataPivot_settings_linedata(self, 0),
                    tbl_line = $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody]);

                tbody.append(obj.tr);

                // Build point table
                headers = ['Column header', 'Display name', 'Marker style', 'Conditional formatting', 'On-click'];
                headers.push('Ordering');
                thead = $('<thead></thead>').html(header_tr(headers));
                var point_tbody = $('<tbody></tbody>');

                var add_point_data_row = function(i){
                        if(!self.settings.datapoint_settings[i]){
                            self.settings.datapoint_settings.push(_DataPivot_settings_pointdata.defaults());
                        }
                        obj = new _DataPivot_settings_pointdata(self, self.settings.datapoint_settings[i]);
                        point_tbody.append(obj.tr);
                    }, new_point_row = function(){
                        var num_rows = self.settings.datapoint_settings.length;
                        add_point_data_row(num_rows);
                    }, num_rows = (self.settings.datapoint_settings.length === 0) ? 3 : self.settings.datapoint_settings.length,
                    new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_point_row),
                    tbl_points = $('<table class="table table-condensed table-bordered"></table>').html([thead, point_tbody]);

                for(var i=0; i<num_rows; i++){
                    add_point_data_row(i);
                }

                return tab.html([
                    '<h3>Data bar options</h3>',
                    tbl_line,
                    $('<h3>Data point options</h3>').append(new_point_button),
                    tbl_points]);
            },
            build_ordering_tab = function(){
                var tab = $('<div class="tab-pane" id="data_pivot_settings_ordering"></div>'),
                    override_tbody = $('<tbody></tbody>'),
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
                                offset_span = $('<span></span>').text(format_offset(obj.offset)),
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
                                [$('<tr></tr>').append(
                                    '<th>Field Name</th>',
                                    '<th>Filter Type</th>',
                                    '<th>Value</th>',
                                    '<th>Ordering</th>')]),
                            tbody = $('<tbody></tbody>'),
                            num_rows = (self.settings.filters.length === 0) ? 2 : self.settings.filters.length,
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
                            new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row);

                        for(var i=0; i<num_rows; i++){
                            add_row(i);
                        }

                        var filter_logic = function(){
                            var lbl = $('<div></div>'),
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

                            return lbl.append('<h4>Filter logic</h4>',
                                              '<p class="help-block">Should multiple filter criteria be required for ALL rows (AND), or ANY row (OR)?</p>',
                                              and, or);
                        }();

                        return div.html([
                            $('<h3>Row Filters</h3>').append(new_point_button),
                            '<p class="help-block">Use filters to determine which components of your dataset should be displayed on the figure.</p>',
                            $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody]),
                            filter_logic]);
                    },
                    build_sorting_div = function(){
                        var div = $('<div></div>'),
                            thead = $('<thead></thead>').html(
                                   [$('<tr></tr>').append('<th>Field Name</th>',
                                                          '<th>Sort Order</th>',
                                                          '<th>Ordering</th>')]),
                            tbody = $('<tbody></tbody>').on('change', 'input,select', function(){
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
                        var div = $('<div></div>'),
                            tbody = $('<tbody></tbody>'),
                            thead = $('<thead></thead>').html(
                                   [$('<tr></tr>').append('<th>Row index</th>',
                                                          '<th>Show line?</th>',
                                                          '<th>Line style</th>',
                                                          '<th>Extra space?</th>',
                                                          '<th>Delete</th>')]),
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
                            new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row);

                        for(var i=0; i<num_rows; i++){
                            add_row(i);
                        }
                        return div.html([
                            $('<h3>Additional Row Spacing</h3>').append(new_point_button),
                            '<p class="help-block">Add additional-space between rows, and optionally a horizontal line.</p>',
                            $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody])]);
                    },
                    build_manual_ordering_div = function(){
                        var div = $('<div></div>'),
                            thead = $('<thead></thead>').html(
                                        [$('<tr></tr>').append(
                                            '<th>Description</th>',
                                            '<th>Include</th>',
                                            '<th>Row Offset</th>',
                                            '<th>Override<br>Text Style</th>',
                                            '<th>Override<br>Line Style</th>',
                                            '<th>Override<br>Symbol Style</th>')]);

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
            },
            build_reference_tab = function(){
                var tab = $('<div class="tab-pane" id="data_pivot_settings_ref"></div>'),
                    build_reference_lines = function(){
                        var thead = $('<thead></thead>').html(
                                [$('<tr></tr>').append('<th>Reference Line Value</th><th>Line Style</th><th>Delete</th>')]),
                            tbody = $('<tbody></tbody>'),
                            add_row = function(i){
                                if(!self.settings.reference_lines[i]){
                                    self.settings.reference_lines.push(_DataPivot_settings_refline.defaults());
                                }
                                var obj = new _DataPivot_settings_refline(self, self.settings.reference_lines[i]);
                                tbody.append(obj.tr);
                            },
                            new_row = function(){
                                var num_rows = self.settings.reference_lines.length;
                                add_row(num_rows);
                            },
                            new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row),
                            num_rows = (self.settings.reference_lines.length === 0) ? 1 : self.settings.reference_lines.length;

                        for(var i=0; i<num_rows; i++){
                            add_row(i);
                        }
                        return $('<div>').append(
                                  $('<h3>Reference Lines</h3>').append(new_point_button),
                                  $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody]));
                    },
                    build_reference_ranges = function(){
                        var thead = $('<thead></thead>').html(
                                [$('<tr></tr>').append('<th>Lower Value</th><th>Upper Value</th><th>Range Style</th><th>Delete</th>')]),
                            colgroup = $('<colgroup><col style="width: 25%;"><col style="width: 25%;"><col style="width: 25%;"><col style="width: 25%;"></colgroup>'),
                            tbody = $('<tbody></tbody>'),
                            add_row = function(i){
                                if(!self.settings.reference_rectangles[i]){
                                    self.settings.reference_rectangles.push(_DataPivot_settings_refrect.defaults());
                                }
                                var obj = new _DataPivot_settings_refrect(self, self.settings.reference_rectangles[i]);
                                tbody.append(obj.tr);
                            },
                            new_row = function(){
                                var num_rows = self.settings.reference_rectangles.length;
                                add_row(num_rows);
                            },
                            new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row),
                            num_rows = (self.settings.reference_rectangles.length === 0) ? 1 : self.settings.reference_rectangles.length;

                        for(var i=0; i<num_rows; i++){
                            add_row(i);
                        }
                        return $('<div>').append(
                            $('<h3>Reference Ranges</h3>').append(new_point_button),
                            $('<table class="table table-condensed table-bordered"></table>').html([colgroup, thead, tbody]));
                    },
                    build_labels = function(){
                        var thead = $('<thead></thead>').html(
                                [$('<tr></tr>').append('<th>Text</th><th>Style</th><th>Delete</th>')]),
                            tbody = $('<tbody></tbody>'),
                            add_row = function(i){
                                if(!self.settings.labels[i]){
                                    self.settings.labels.push(_DataPivot_settings_label.defaults());
                                }
                                var obj = new _DataPivot_settings_label(self, self.settings.labels[i]);
                                tbody.append(obj.tr);
                            },
                            new_row = function(){
                                var num_rows = self.settings.labels.length;
                                add_row(num_rows);
                            },
                            new_point_button = $('<button class="btn btn-primary pull-right">New Row</button>').on('click', new_row),
                            num_rows = (self.settings.labels.length === 0) ? 1 : self.settings.labels.length;

                        for(var i=0; i<num_rows; i++){
                            add_row(i);
                        }
                        return $('<div>').append(
                                $('<h3>Labels</h3>').append(new_point_button),
                                $('<table class="table table-condensed table-bordered"></table>').html([thead, tbody]));
                    };

                return tab.html([
                    build_reference_lines(),
                    build_reference_ranges(),
                    build_labels(),
                ]);
            },
            build_styles_tab = function(){
                var tab = $('<div class="tab-pane" id="data_pivot_settings_styles"></div>'),
                    symbol_div = self.style_manager.build_styles_crud('symbols'),
                    line_div = self.style_manager.build_styles_crud('lines'),
                    text_div  = self.style_manager.build_styles_crud('texts'),
                    rectangle_div  = self.style_manager.build_styles_crud('rectangles');

                return tab.html([
                    symbol_div, '<hr>',
                    line_div, '<hr>',
                    text_div, '<hr>',
                    rectangle_div,
                ]);
            },
            build_settings_general_tab = function(){
                var tab = $('<div class="tab-pane" id="data_pivot_settings_general"></div>'),
                    build_general_settings = function(){
                        var div = $('<div></div>'),
                            tbl = $('<table class="table table-condensed table-bordered"></table>'),
                            tbody = $('<tbody></tbody>'),
                            colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;"></colgroup>');

                        self._dp_settings_general = new _DataPivot_settings_general(self, self.settings.plot_settings);
                        tbody.html(self._dp_settings_general.trs);
                        tbl.html([colgroup, tbody]);
                        return div.html(tbl);
                    },
                    build_download_button = function(){
                        return $('<button class="btn btn-primary">Download settings</button>')
                          .on('click', function(){self.download_settings();});
                    },
                    build_legend_settings = function(){
                        var div = $('<div class="row-fluid"></div>'),
                            content = $('<div class="span6"></div>'),
                            plot_div = $('<div class="span6"></div>'),
                            vis = d3.select(plot_div[0])
                                      .append('svg')
                                          .attr('width', '95%')
                                          .attr('height', '300px')
                                          .attr('class', 'd3')
                                      .append('g')
                                          .attr('transform', 'translate(10,10)');

                        self.legend = new DataPivotLegend(vis, self.settings.legend, self.settings);

                        var tbl = $('<table class="table table-condensed table-bordered"></table>'),
                            tbody = $('<tbody>'),
                            colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;"></colgroup>'),
                            build_tr = function(label, input){
                                return $('<tr>').append('<th>{0}</th>'.printf(label))
                                    .append($('<td>').append(input));
                            },
                            add_horizontal_field = function(label_text, html_obj){
                                return $('<div class="control-group"></div>')
                                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                                    .append( $('<div class="controls"></div>').append(html_obj));
                            },
                            show_legend = $('<input type="checkbox">')
                                .prop('checked', self.settings.legend.show)
                                .on('change', function(){ self.settings.legend.show = $(this).prop('checked');}),
                            number_columns = $('<input>')
                                .val(self.settings.legend.columns)
                                .on('change', function(){
                                    self.settings.legend.columns = parseInt($(this).val(), 10) || 1;
                                    self.legend._draw_legend();
                                }),
                            left = $('<input>')
                                .val(self.settings.legend.left)
                                .on('change', function(){
                                    self.settings.legend.left = parseInt($(this).val(), 10) || 1;
                                    self.legend._draw_legend();
                                }),
                            top = $('<input>')
                                .val(self.settings.legend.top)
                                .on('change', function(){
                                    self.settings.legend.top = parseInt($(this).val(), 10) || 1;
                                    self.legend._draw_legend();
                                }),
                            border_width = $('<input type="range" min="0" max="10" value="{0}">'
                                    .printf(self.settings.legend.style.border_width))
                                .on('change', function(){
                                    self.settings.legend.style.border_width = parseFloat($(this).val(), 10) || 0;
                                    self.legend._draw_legend();
                                }),
                            border_color = $('<input name="fill" type="color" value="{0}">'
                                    .printf(self.settings.legend.style.border_color))
                                .on('change', function(){
                                    self.settings.legend.style.border_color = $(this).val();
                                    self.legend._draw_legend();
                                }),
                            modal = $('<div class="modal hide fade">' +
                                      '<div class="modal-header">' +
                                          '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
                                          '<h3>Modify Legend Entry</h3>' +
                                      '</div>' +
                                      '<div class="modal-body">' +
                                      '<form class="form-horizontal">' +
                                        '<div class="style_plot" style="margin-left:180px; height: 70px;"></div><br>' +
                                        '<div class="legend_fields"></div>' +
                                      '</div>' +
                                      '<div class="modal-footer">' +
                                          '<button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>' +
                                      '</div>' +
                                    '</div>'),
                            button_well = $('<div class="well"></div>'),
                            draw_modal_fields = function(d){
                                if(d){
                                    modal.data('d', d);
                                } else{
                                    modal.removeData('d');
                                }
                                var tmp_label = (d) ? d.label : NULL_CASE,
                                    tmp_line = (d) ? d.line_style : NULL_CASE,
                                    tmp_symbol = (d) ? d.symbol_style : NULL_CASE,
                                    name = $('<input name="legend_name" value="{0}">'.printf(tmp_label)),
                                    line = self.style_manager.add_select('lines', tmp_line, true)
                                                .removeClass('span12').attr('name', 'legend_line'),
                                    symbol = self.style_manager.add_select('symbols', tmp_symbol, true)
                                                .removeClass('span12').attr('name', 'legend_symbol');

                                modal.find('.legend_fields').html([
                                    add_horizontal_field('Legend Name', name),
                                    add_horizontal_field('Symbol Style', symbol),
                                    add_horizontal_field('Line Style', line)]);

                                var svgdiv = modal.find('.style_plot'),
                                    build_style_obj = function(){
                                        return {
                                            type: 'legend',
                                            line_style: line.find('option:selected').data('d'),
                                            symbol_style: symbol.find('option:selected').data('d'),
                                        };
                                    }, viewer = new StyleViewer(svgdiv, build_style_obj()),
                                    update_viewer = function(){
                                        viewer.apply_new_styles(build_style_obj(), false);
                                    };

                                line.on('change', update_viewer);
                                symbol.on('change', update_viewer);
                            },
                            legend_item = self.legend.add_select(),
                            legend_item_up = $('<button><i class="icon-arrow-up"></i></button>')
                                .on('click', function(){
                                    self.legend.move_field(legend_item.find('option:selected').data('d'), -1);
                                    self.legend._draw_legend();
                                }),
                            legend_item_down = $('<button><i class="icon-arrow-down"></i></button>')
                                .on('click', function(){
                                    self.legend.move_field(legend_item.find('option:selected').data('d'), 1);
                                    self.legend._draw_legend();
                                }),
                            legend_item_new = $('<button class="btn btn-primary">New</button>')
                                .on('click', function(){
                                    modal.modal('show');
                                    draw_modal_fields(undefined);
                                    self.legend._draw_legend();
                                }),
                            legend_item_edit = $('<button class="btn btn-info">Edit</button>')
                                .on('click', function(){
                                    modal.modal('show');
                                    draw_modal_fields(legend_item.find('option:selected').data('d'));
                                    self.legend._draw_legend();
                                }),
                            legend_item_delete = $('<button class="btn btn-danger">Delete</button>')
                                .on('click', function(){
                                    self.legend.delete_field(legend_item.find('option:selected').data('d'));
                                    self.legend._draw_legend();
                                }),
                            save_legend_item = $('<button class="btn btn-primary"aria-hidden="true">Save and Close</button>')
                                .on('click', function(){
                                    var label = modal.find('input[name="legend_name"]').val(),
                                        line_style = modal.find('select[name="legend_line"] option:selected').val(),
                                        symbol_style = modal.find('select[name="legend_symbol"] option:selected').val();

                                    if((label === '') ||
                                       ((line_style === NULL_CASE) &&
                                        (symbol_style === NULL_CASE))){
                                        alert('Error - name must not be blank, and at least one style must be selected');
                                        return;
                                    }

                                    var d = modal.data('d'),
                                        obj = {line_style, symbol_style, label};

                                    self.legend.add_or_update_field(obj, d);
                                    modal.modal('hide');
                                    self.legend._draw_legend();
                                });

                        modal.find('.modal-footer').append(save_legend_item);
                        tbody.html([
                            build_tr('Show legend', show_legend),
                            build_tr('Number of columns', number_columns),
                            build_tr('Border width', DataPivot.rangeInputDiv(border_width)),
                            build_tr('Border color', border_color),
                            build_tr('X-location on figure', left),
                            build_tr('Y-location on figure', top),
                            build_tr('Legend item', legend_item),
                        ]);

                        tbl.html([colgroup, tbody]);
                        button_well.append(
                            legend_item_new,
                            legend_item_up,
                            legend_item_down,
                            legend_item_edit,
                            legend_item_delete);
                        content.append('<h4>Legend Settings<h4>', tbl, button_well);
                        div.html([content, plot_div]);
                        div.find('input[type="color"]')
                            .spectrum({showInitial: true, showInput: true});
                        return div;
                    };

                // update whenever tab is clicked
                var legend_div = build_legend_settings();
                self.$div.on('shown','a.dp_general_tab[data-toggle="tab"]', function(){
                    self.legend._draw_legend();
                });

                return tab.html([
                    build_general_settings(), '<hr>',
                    legend_div, '<hr>',
                    build_download_button(),
                ]);
            },
            content = [
                $('<ul class="nav nav-tabs">')
                    .append(
                        '<li class="active"><a href="#data_pivot_settings_description" data-toggle="tab">Description Columns</a></li>',
                        '<li><a href="#data_pivot_settings_data" data-toggle="tab">Data Columns</a></li>',
                        '<li><a class="dp_ordering_tab" href="#data_pivot_settings_ordering" data-toggle="tab">Row Ordering</a></li>',
                        '<li><a href="#data_pivot_settings_ref" data-toggle="tab">References</a></li>',
                        '<li><a href="#data_pivot_settings_styles" data-toggle="tab">Styles</a></li>',
                        '<li><a class="dp_general_tab" href="#data_pivot_settings_general" data-toggle="tab">General Settings</a></li>'),
                $('<div class="tab-content"></div>')
                    .append(
                        build_description_tab(),
                        build_settings_general_tab(),
                        build_data_tab(),
                        build_ordering_tab(),
                        build_reference_tab(),
                        build_styles_tab()),
            ];

        this.$settings_div
          .html(content)
          .on('shown', function(e){
              if($(e.target).attr('href') === '#data_pivot_settings_general'){
                  self._dp_settings_general.update_merge_until();
              }
          });
    }

    _get_header_options(show_blank){
        var opts = [];
        if (show_blank) opts.push('<option value="{0}">{0}</option>'.printf(NULL_CASE));
        return opts.concat(this.data_headers.map(function(v){
            return '<option value="{0}">{0}</option>'.printf(v);
        }));
    }

    _get_description_options(){
        return this.settings.description_settings.map(function(d,i){
            return '<option value="{0}">{1}</option>'.printf(i, d.header_name);
        });
    }

    download_settings(){
        var settings_json = this.get_settings_json();
        saveTextAs(settings_json, 'data_pivot_settings.json');
    }

    get_settings_json(){
        return JSON.stringify(this.settings);
    }

    displayAsModal(){
        var self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.title),
            $plot = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">')
                    .append($plot));

        modal.getModal().on('shown', function(){
            self.build_data_pivot_vis($plot);
        });

        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show();
    }

    object_hyperlink(){
        return $('<a>')
            .attr('href', this.url)
            .attr('target', '_blank')
            .text(this.title);
    }
}

export default DataPivot;
