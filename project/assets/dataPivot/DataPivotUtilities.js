import $ from '$';
import _ from 'underscore';
import d3 from 'd3';

import DataPivot from './DataPivot';
import DataPivotVisualization from './DataPivotVisualization';
import {
   NULL_CASE,
} from './shared';


class _DataPivot_settings_refline {

    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {};
        this.content.value_field = $('<input class="span12" type="text">');

        this.content.line_style = this.data_pivot.style_manager
            .add_select('lines', values.line_style);

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.reference_lines, this, {showSort: false});

        // set default values
        this.content.value_field.val(values.value);

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.value_field))
            .append($('<td>').append(this.content.line_style))
            .append(movement_td)
            .on('change', 'input,select', function(v){self.data_push();});

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            value: NULL_CASE,
            line_style: 'reference line',
        };
    }

    data_push(){
        this.values.value = parseFloat(this.content.value_field.val());
        this.values.line_style = this.content.line_style.find('option:selected').text();
    }
}


class _DataPivot_settings_refrect {

    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {};
        this.content.x1_field = $('<input class="span12" type="text">');
        this.content.x2_field = $('<input class="span12" type="text">');
        this.content.rectangle_style = this.data_pivot.style_manager
            .add_select('rectangles', values.rectangle_style);

        // set default values
        this.content.x1_field.val(values.x1);
        this.content.x2_field.val(values.x2);

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.reference_rectangles, this, {showSort: false});

        this.tr = $('<tr></tr>')
            .append($('<td></td>').append(this.content.x1_field))
            .append($('<td></td>').append(this.content.x2_field))
            .append($('<td></td>').append(this.content.rectangle_style))
            .append(movement_td)
            .on('change', 'input,select', function(v){self.data_push();});

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'x1': NULL_CASE,
            'x2': NULL_CASE,
            'rectangle_style': 'base',
        };
    }

    data_push(){
        this.values.x1 = parseFloat(this.content.x1_field.val());
        this.values.x2 = parseFloat(this.content.x2_field.val());
        this.values.rectangle_style = this.content.rectangle_style.find('option:selected').text();
    }
}


class _DataPivot_settings_label {

    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {};
        this.content.text = $('<input class="span12" type="text">').val(values.text);
        this.content.style = this.data_pivot.style_manager.add_select('texts', values.style);

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.labels, this, {showSort: false});

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.text))
            .append($('<td>').append(this.content.style))
            .append(movement_td)
            .on('change', 'input,select', function(v){self.data_push();});

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'text': '',
            'style': 'title',
            'x': 10,
            'y': 10,
        };
    }

    data_push(){
        this.values.text = this.content.text.val();
        this.values.style = this.content.style.find('option:selected').text();
    }
}


class _DataPivot_settings_sorts {

    constructor(data_pivot, values, index){
        var self = this,
            movement_td = DataPivot.build_movement_td(data_pivot.settings.sorts, this, {showSort: true});
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {};
        this.content.field_name = $('<select class="span12"></select>')
            .html(this.data_pivot._get_header_options(true));
        this.content.ascending = $('<label class="radio"><input name="asc{0}" type="radio" value="true">Ascending</label><label class="radio"><input name="asc{0}" type="radio" value="false">Descending</label>'.printf(index));

        // set default values
        this.content.field_name
            .find('option[value="{0}"]'.printf(values.field_name))
            .prop('selected', true);
        this.content.ascending.find('[value={0}]'.printf(values.ascending)).prop('checked', true);

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.field_name))
            .append($('<td>').append(this.content.ascending))
            .append(movement_td)
            .on('change', 'input,select', function(v){self.data_push();});

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'field_name': NULL_CASE,
            'ascending': true,
        };
    }

    data_push(){
        this.values.field_name=this.content.field_name.find('option:selected').text();
        this.values.ascending=this.content.ascending.find('input').prop('checked');
    }
}


class _DataPivot_settings_filters {

    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        var get_quantifier_options = function(){
            return '<option value="gt">&gt;</option>' +
                   '<option value="gte">≥</option>' +
                   '<option value="lt">&lt;</option>' +
                   '<option value="lte">≤</option>' +
                   '<option value="exact">exact</option>' +
                   '<option value="contains">contains</option>' +
                   '<option value="not_contains">does not contain</option>';
        };

        // create fields
        this.content = {};
        this.content.field_name = $('<select class="span12"></select>')
            .html(this.data_pivot._get_header_options(true));
        this.content.quantifier = $('<select class="span12"></select>')
            .html(get_quantifier_options());
        this.content.value = $('<input class="span12" type="text">').autocomplete({'source': values.value});

        // set default values
        this.content.field_name
            .find('option[value="{0}"]'.printf(values.field_name))
            .prop('selected', true);
        this.content.quantifier
            .find('option[value="{0}"]'.printf(values.quantifier))
            .prop('selected', true);
        this.content.value.val(values.value);

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.filters, this, {showSort: true});

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.field_name))
            .append($('<td>').append(this.content.quantifier))
            .append($('<td>').append(this.content.value))
            .append(movement_td)
            .on('change autocompletechange autocompleteselect', 'input,select', function(v){self.data_push();});

        var content = this.content,
            enable_autocomplete = function(request, response){
                var field = content.field_name.find('option:selected').val(),
                    values = d3.set(data_pivot.data.map(function(v){ return v[field];})).values();
                content.value.autocomplete('option', {'source': values});
            };

        this.content.field_name.on('change', enable_autocomplete);
        enable_autocomplete();

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'field_name': NULL_CASE,
            'quantifier': 'contains',
            'value': '',
        };
    }

    data_push(){
        this.values.field_name = this.content.field_name.find('option:selected').val();
        this.values.quantifier = this.content.quantifier.find('option:selected').val();
        this.values.value = this.content.value.val();
    }
}


class _DataPivot_settings_spacers {
    constructor(data_pivot, values, index){
        var self = this,
            movement_td = DataPivot.build_movement_td(data_pivot.settings.spacers, this, {showSort: false});

        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {
            index: $('<input class="span12" type="number">'),
            show_line: $('<input type="checkbox">'),
            line_style: data_pivot.style_manager.add_select('lines', values.line_style),
            extra_space: $('<input type="checkbox">'),
        };

        // set default values
        this.content.index.val(values.index);
        this.content.show_line.prop('checked', values.show_line);
        this.content.extra_space.prop('checked', values.extra_space);

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.index))
            .append($('<td>').append(this.content.show_line))
            .append($('<td>').append(this.content.line_style))
            .append($('<td>').append(this.content.extra_space))
            .append(movement_td)
            .on('change', 'input,select', function(v){self.data_push();});

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            index: NULL_CASE,
            show_line: true,
            line_style: 'reference line',
            extra_space: false,
        };
    }

    data_push(){
        this.values.index = parseInt(this.content.index.val(), 10) || -1;
        this.values.show_line = this.content.show_line.prop('checked');
        this.values.line_style = this.content.line_style.find('option:selected').text();
        this.values.extra_space = this.content.extra_space.prop('checked');
    }
}


class _DataPivot_settings_description {
    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {
            field_name :$('<select class="span12"></select>').html(this.data_pivot._get_header_options(true)),
            header_name: $('<input class="span12" type="text">'),
            header_style: this.data_pivot.style_manager.add_select('texts', values.header_style),
            text_style: this.data_pivot.style_manager.add_select('texts', values.text_style),
            max_width: $('<input class="span12" type="number">'),
            dpe: $('<select class="span12"></select>').html(this.data_pivot.dpe_options),
        };

        // set default values
        this.content.field_name.find('option[value="{0}"]'.printf(values.field_name)).prop('selected', true);
        this.content.header_name.val(values.header_name);
        this.content.max_width.val(values.max_width);
        this.content.dpe.find('option[value="{0}"]'.printf(values.dpe)).prop('selected', true);

        var header_input = this.content.header_name;
        this.content.field_name.on('change', function(){
            header_input.val($(this).find('option:selected').val());
        });

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.field_name))
            .append($('<td>').append(this.content.header_name))
            .append($('<td>').append(this.content.header_style))
            .append($('<td>').append(this.content.text_style))
            .append($('<td>').append(this.content.max_width))
            .append($('<td>').append(this.content.dpe))
            .on('change', 'input,select', function(v){self.data_push();});

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.description_settings, this, {showSort: true});
        this.tr.append(movement_td);

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'field_name': NULL_CASE,
            'header_name': '',
            'header_style': 'header',
            'text_style': 'base',
            'dpe': NULL_CASE,
            'max_width': undefined,
        };
    }

    data_push(){
        this.values.field_name =  this.content.field_name.find('option:selected').val();
        this.values.field_index = this.content.field_name.find('option:selected').val();
        this.values.header_style = this.content.header_style.find('option:selected').val();
        this.values.text_style = this.content.text_style.find('option:selected').val();
        this.values.header_name = this.content.header_name.val();
        this.values.max_width = parseFloat(this.content.max_width.val(), 10) || undefined;
        this.values.dpe = NULL_CASE;
        if(this.values.header_name === ''){this.values.header_name = this.values.field_name;}
        if(this.content.dpe){this.values.dpe = this.content.dpe.find('option:selected').val();}
    }
}


class _DataPivot_settings_pointdata {
    constructor(data_pivot, values){
        var self = this,
            style_type = 'symbols';

        this.data_pivot = data_pivot;
        this.values = values;
        this.conditional_formatter = new _DataPivot_settings_conditionalFormat(this, values.conditional_formatting || []);

        // create fields
        this.content = {
            'field_name': $('<select class="span12">').html(this.data_pivot._get_header_options(true)),
            'header_name': $('<input class="span12" type="text">'),
            'marker_style': this.data_pivot.style_manager.add_select(style_type, values.marker_style),
            'conditional_formatting': this.conditional_formatter.data,
            'dpe': $('<select class="span12"></select>').html(this.data_pivot.dpe_options),
        };

        // set default values
        this.content.field_name.find('option[value="{0}"]'.printf(values.field_name)).prop('selected', true);
        this.content.header_name.val(values.header_name);
        this.content.dpe.find('option[value="{0}"]'.printf(values.dpe)).prop('selected', true);

        var header_input = this.content.header_name;
        this.content.field_name.on('change', function(){
            header_input.val($(this).find('option:selected').val());
        });

        this.tr = $('<tr>')
            .append($('<td>').append(this.content.field_name))
            .append($('<td>').append(this.content.header_name))
            .append($('<td>').append(this.content.marker_style))
            .append($('<td>').append(this.conditional_formatter.status))
            .append($('<td>').append(this.content.dpe))
            .on('change', 'input,select', function(v){
                //update self
                self.data_push();
                // update legend
                var obj = {'symbol_index': self.data_pivot.settings.datapoint_settings.indexOf(values),
                           'label': self.content.header_name.val(),
                           'symbol_style': self.content.marker_style.find('option:selected').text()};
                self.data_pivot.legend.add_or_update_field(obj);
            });

        var movement_td = DataPivot.build_movement_td(self.data_pivot.settings.datapoint_settings, this, {showSort: true});
        this.tr.append(movement_td);

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'field_name': NULL_CASE,
            'header_name': '',
            'marker_style': 'base',
            'dpe': NULL_CASE,
            'conditional_formatting': [],
        };
    }

    data_push(){
        this.values.field_name = this.content.field_name.find('option:selected').val();
        this.values.header_name = this.content.header_name.val();
        this.values.marker_style = this.content.marker_style.find('option:selected').text();
        this.values.dpe = NULL_CASE;
        this.values.conditional_formatting = this.conditional_formatter.data;
        if(this.values.header_name === ''){this.values.header_name = this.values.field_name;}
        if(this.content.dpe){this.values.dpe = this.content.dpe.find('option:selected').val();}
    }
}


class _DataPivot_settings_conditionalFormat {

    constructor(parent, values){
        var self = this;

        this.parent = parent;
        this.data = values;
        this.status = $('<div>');
        this.conditionals = [];
        this.modalInitialized = false;

        this._status_text = $('<span style="padding-right: 10px">')
          .appendTo(this.status);

        this._showModal = $('<button class="btn btn-small" type="button">')
          .on('click', function(){self._show_modal();})
          .appendTo(this.status);

        this._update_status();
        this._build_modal();
    }

    _update_status(){
        var status = (this.data.length>0) ? 'Enabled' : 'None',
            modal =  (this.data.length>0) ? 'Edit' : 'Create';

        this._status_text.text(status);
        this._showModal.text(modal);
    }

    _build_modal(){
        this.modal = $('<div class="modal hide fade">').appendTo(this.status);
    }

    _show_modal(){
        // set header text
        var txt = 'Conditional formatting: <i>{0}<i>'.printf(this.parent.values.field_name);
        this.modal.find('.modal-header').empty()
            .append($('<h4>').html(txt));

        // load current conditions
        if (!this.modalInitialized) this._draw_conditions();
        this.modalInitialized = true;

        // show modal
        this.modal.modal('show');
    }

    close_modal(save){
        if(save) this._save_conditions();
        this._update_status();
        this.modal.modal('hide');
    }

    _draw_conditions(){
        var self = this,
            body = this.modal.find('.modal-body').empty();

        // add placeholder if no conditions are set
        this.blank = $('<span>').appendTo(body);
        if(this.data.length === 0) this.blank.text('No conditions have been set.');

        // draw conditions
        this.data.forEach(function(v){
            self.conditionals.push(new _DataPivot_settings_conditional(body, self, v));
        });
    }

    _save_conditions(){
        this.data = this.conditionals.map(function(v){ return v.get_values(); });
        this.parent.data_push();
    }

    _add_condition(values){
        var body = this.modal.find('.modal-body');
        this.blank.empty();
        this.conditionals.push(new _DataPivot_settings_conditional(body, this, values));
    }

    delete_condition(conditional){
        this.conditionals.splice_object(conditional);
    }
}
_.extend(_DataPivot_settings_conditionalFormat, {
    condition_types: [
        'point-size',
        'point-color',
        'discrete-style',
    ],
    defaults: {
        field_name: NULL_CASE,
        condition_type: 'point-size',
        min_size: 50,
        max_size: 150,
        min_color: '#800000',
        max_color: '#008000',
        discrete_styles: [],
    },
});

class _DataPivot_ColorGradientSVG {
    constructor(svg, start_color, stop_color){
        svg = d3.select(svg);
        var gradient = svg.append('svg:defs')
          .append('svg:linearGradient')
            .attr('id', 'gradient')
            .attr('x1', '0%')
            .attr('y1', '100%')
            .attr('x2', '100%')
            .attr('y2', '100%')
            .attr('spreadMethod', 'pad');

        this.start = gradient.append('svg:stop')
            .attr('offset', '0%')
            .attr('stop-color', start_color)
            .attr('stop-opacity', 1);

        this.stop = gradient.append('svg:stop')
            .attr('offset', '100%')
            .attr('stop-color', stop_color)
            .attr('stop-opacity', 1);

        svg.append('svg:rect')
            .attr('width', '100%')
            .attr('height', '100%')
            .style('fill', 'url(#gradient)');
    }

    update_start_color(color){
        this.start.attr('stop-color', color);
    }

    update_stop_color(color){
        this.stop.attr('stop-color', color);
    }
}


class _DataPivot_settings_conditional {
    constructor(parent_div, parent, values){
        values = values || {discrete_styles: []};
        this.inputs = [];

        var self = this,
            dp = parent.parent.data_pivot,
            defaults = _DataPivot_settings_conditionalFormat.defaults,
            div = $('<div class="well">')
                    .appendTo(parent_div),
            add_input_row = function(parent, desc_txt, inp){
                var lbl = $('<label>').html(desc_txt);
                parent.append(lbl, inp);
            },
            fieldName = $('<select name="field_name">')
                .html(dp._get_header_options(true))
                .val(values.field_name || defaults.field_name),
            conditionType = $('<select name="condition_type">')
                .html(_DataPivot_settings_conditionalFormat.condition_types.map(function(v){
                    return '<option value="{0}">{0}</option>'.printf(v);
                }))
                .val(values.condition_type || defaults.condition_type),
            changeConditionType = function(){
                div.find('.conditionalDivs').hide();
                div.find('.' + conditionType.val()).fadeIn();
            };

        // add delete button
        $('<button type="button" class="close">')
          .text('x')
          .on('click', function(){
              div.remove();
              parent.delete_condition(self);
          })
          .prependTo(div); // todo pop from parent

        // add master conditional inputs and divs for changing fields
        add_input_row(div, 'Condition field', fieldName);
        add_input_row(div, 'Condition type', conditionType);
        div.append('<hr>');
        _DataPivot_settings_conditionalFormat.condition_types.forEach(function(v){
            $('<div class="conditionalDivs {0}">'.printf(v)).appendTo(div).hide();
        });

        // build min/max for size and color
        var min_size = $('<input name="min_size" type="range" min="0" max="500" step="5">')
            .val(values.min_size || defaults.min_size),
            max_size = $('<input name="max_size" type="range" min="0" max="500" step="5">')
              .val(values.max_size || defaults.max_size),
            min_color = $('<input name="min_color" type="color">')
              .val(values.min_color || defaults.min_color),
            max_color = $('<input name="max_color" type="color">')
              .val(values.max_color || defaults.max_color),
            svg = $('<svg width="150" height="25" class="d3" style="margin-top: 10px"></svg>'),
            gradient = new _DataPivot_ColorGradientSVG(svg[0], min_color.val(), max_color.val());

        // add event-handlers to change gradient color
        min_color.change(function(v){gradient.update_start_color(min_color.val());});
        max_color.change(function(v){gradient.update_stop_color(max_color.val());});

        // add size values to size div
        var ps = div.find('.point-size'),
            min_max_ps = $('<p>').appendTo(ps);
        add_input_row(ps, 'Minimum point-size', DataPivot.rangeInputDiv(min_size));
        add_input_row(ps, 'Maximum point-size', DataPivot.rangeInputDiv(max_size));

        // add color values to color div
        var pc = div.find('.point-color'),
            min_max_pc = $('<p>').appendTo(pc);
        add_input_row(pc, 'Minimum color', min_color);
        add_input_row(pc, 'Maximum color', max_color);
        pc.append('<br>', svg);
        div.find('input[type="color"]').spectrum({'showInitial': true, 'showInput': true});

        this.inputs.push(fieldName, conditionType,
                         min_size, max_size,
                         min_color, max_color);

        // get unique values and set values
        var buildStyleSelectors = function(){
            // show appropriate div
            var discrete = div.find('.discrete-style');
            self.discrete_styles = [];
            discrete.empty();

            var subset = DataPivotVisualization.filter(dp.data, dp.settings.filters, dp.settings.plot_settings.filter_logic),
                arr = subset.map(function(v){return v[fieldName.val()]; }),
                vals = DataPivot.getRowDetails(arr);

            if (conditionType.val() === 'discrete-style'){
                // make map of current values
                var hash = d3.map();
                values.discrete_styles.forEach(function(v){
                    hash.set(v.key, v.style);
                });

                vals.unique.forEach(function(v){
                    var style = dp.style_manager
                                  .add_select('symbols', hash.get(v), true)
                                  .data('key', v);
                    self.discrete_styles.push(style);
                    add_input_row(discrete, 'Style for <i>{0}</i>:'.printf(v), style);
                });
            } else {
                var txt = 'Selected items in <i>{0}</i> '.printf(fieldName.val());
                if(vals.range){
                    txt += 'contain values ranging from {0} to {1}.'.printf(vals.range[0], vals.range[1]);
                } else {
                    txt += 'have no range of values, please select another column.';
                }

                min_max_pc.html(txt);
                min_max_ps.html(txt);
            }
        };

        // add event-handlers and fire to initialize
        fieldName.on('change', buildStyleSelectors);
        conditionType.on('change', function(){
            buildStyleSelectors();
            changeConditionType();
        });

        changeConditionType();
        buildStyleSelectors();
    }

    get_values(){
        var values = {'discrete_styles': []};
        this.inputs.forEach(function(v){
            values[v.attr('name')] = parseInt(v.val(), 10) || v.val();
        });
        this.discrete_styles.forEach(function(v){
            values.discrete_styles.push({ key: v.data('key'), style: v.val()});
        });
        return values;
    }
}


class _DataPivot_settings_linedata {
    constructor(data_pivot, index){
        var self = this,
            style_type = 'lines',
            values = data_pivot.settings.dataline_settings[index];

        this.data_pivot = data_pivot;
        this.index = index;

        // create fields
        this.content = {
            'low_field_name': $('<select class="span12"></select>').html(this.data_pivot._get_header_options(true)),
            'high_field_name': $('<select class="span12"></select>').html(this.data_pivot._get_header_options(true)),
            'header_name': $('<input  class="span12" type="text">'),
            'marker_style': this.data_pivot.style_manager.add_select(style_type, values.marker_style)};

        // set default values
        this.content.low_field_name.find('option[value="{0}"]'
            .printf(values.low_field_name))
            .prop('selected', true);

        this.content.high_field_name.find('option[value="{0}"]'
            .printf(values.high_field_name))
            .prop('selected', true);

        this.content.header_name.val(values.header_name);

        var header_input = this.content.header_name;
        this.content.low_field_name.on('change', function(){
            header_input.val($(this).find('option:selected').val());
        });

        this.tr = $('<tr>')
            .append($('<td>').append('<b>Low Range:</b><br>',
                                          this.content.low_field_name,
                                          '<br><b>High Range:</b><br>',
                                          this.content.high_field_name))
            .append($('<td>').append(this.content.header_name))
            .append($('<td>').append(this.content.marker_style))
            .on('change', 'input,select', function(v){
                self.data_push();

                // update legend
                var obj = {'line_index': index,
                           'label': self.content.header_name.val(),
                           'line_style': self.content.marker_style.find('option:selected').text()};
                self.data_pivot.legend.add_or_update_field(obj);
            });

        this.data_push();
        return this;
    }

    static defaults(){
        return {
            'low_field_name': NULL_CASE,
            'high_field_name': NULL_CASE,
            'header_name': '',
            'marker_style': 'base',
        };
    }

    data_push(){
        var v = {
            'low_field_name': this.content.low_field_name.find('option:selected').val(),
            'high_field_name': this.content.high_field_name.find('option:selected').val(),
            'header_name': this.content.header_name.val(),
            'marker_style': this.content.marker_style.find('option:selected').text(),
        };

        if (v.header_name === ''){v.header_name = v.low_field_name;}
        this.data_pivot.settings.dataline_settings[this.index] = v;
    }
}


class _DataPivot_settings_general {
    constructor(data_pivot, values){
        var self = this;
        this.data_pivot = data_pivot;
        this.values = values;

        // create fields
        this.content = {
            'plot_width': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.plot_width)),
            'minimum_row_height': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.minimum_row_height)),
            'title': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.title)),
            'axis_label': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.axis_label)),
            'show_xticks': $('<input type="checkbox">').prop('checked', values.show_xticks),
            'show_yticks': $('<input type="checkbox">').prop('checked', values.show_yticks),
            'font_style': $('<select></select>')
                .append('<option value="Arial">Arial</option>',
                        '<option value="Times New Roman">Times New Roman</option>'),
            'logscale': $('<input type="checkbox">').prop('checked', values.logscale),
            'domain': $('<input class="input-xlarge" title="Print the minimum value, a comma, and then the maximum value" type="text" value="{0}">'.printf(values.domain)),
            'padding_top': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.padding.top)),
            'padding_right': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.padding.right)),
            'padding_bottom': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.padding.bottom)),
            'padding_left': $('<input class="input-xlarge" type="text" value="{0}">'.printf(values.padding.left)),
            'merge_descriptions': $('<input type="checkbox">').prop('checked', values.merge_descriptions),
            'merge_aggressive': $('<input type="checkbox">').prop('checked', values.merge_aggressive),
            'merge_until': $('<select name="merge_until">'),
            'text_background': $('<input type="checkbox">').prop('checked', values.text_background),
            'text_background_color': $('<input type="color">').val(values.text_background_color),
        };

        // set default values
        this.content.font_style.find('option[value="{0}"]'.printf(values.font_style)).prop('selected', true);
        this.update_merge_until();

        var build_tr = function(name, content){
            return $('<tr>').append($('<th>{0}</th>'.printf(name)),
                                     $('<td>').append(content))
                .on('change', 'input,select', function(v){self.data_push();});
        };

        this.trs = [
            build_tr('Plot width', this.content.plot_width),
            build_tr('Minimum row height', this.content.minimum_row_height),
            build_tr('Font style', this.content.font_style),
            build_tr('Title', this.content.title),
            build_tr('X-axis label', this.content.axis_label),
            build_tr('Show x-axis ticks', this.content.show_xticks),
            build_tr('Show y-axis ticks', this.content.show_yticks),
            build_tr('Logscale', this.content.logscale),
            build_tr('Axis minimum and maximum<br>(ex: "1,100")', this.content.domain),
            build_tr('Plot padding top', this.content.padding_top),
            build_tr('Plot padding right', this.content.padding_right),
            build_tr('Plot padding bottom', this.content.padding_bottom),
            build_tr('Plot padding left', this.content.padding_left),
            build_tr('Merge descriptions', this.content.merge_descriptions),
            build_tr('Merge descriptions up to', this.content.merge_until),
            build_tr('Merge aggressively', this.content.merge_aggressive),
            build_tr('Highlight background text', this.content.text_background),
            build_tr('Highlight background text color', this.content.text_background_color)];

        this.content.text_background_color
            .spectrum({'showInitial': true, 'showInput': true});

        // display merge_until only when merge_descriptions activated
        var show_mergeUntil = function(){
            var show = self.content.merge_descriptions.prop('checked'),
                row1 = self.content.merge_until.parent().parent(),
                row2 = self.content.merge_aggressive.parent().parent();
            if (show){
                row1.show();
                row2.show();
            } else {
                row1.hide();
                row2.hide();
            }
        };
        this.content.merge_descriptions.on('change', show_mergeUntil);
        show_mergeUntil();

        this.data_push();
        return this;
    }

    data_push(){
        this.values.plot_width = parseInt(this.content.plot_width.val(), 10);
        this.values.minimum_row_height = parseInt(this.content.minimum_row_height.val(), 10);
        this.values.font_style = this.content.font_style.find('option:selected').val();
        this.values.title = this.content.title.val();
        this.values.axis_label = this.content.axis_label.val();
        this.values.show_xticks = this.content.show_xticks.prop('checked');
        this.values.show_yticks = this.content.show_yticks.prop('checked');
        this.values.logscale = this.content.logscale.prop('checked');
        this.values.domain = this.content.domain.val();
        this.values.padding.top = parseInt(this.content.padding_top.val(), 10);
        this.values.padding.right = parseInt(this.content.padding_right.val(), 10);
        this.values.padding.bottom = parseInt(this.content.padding_bottom.val(), 10);
        this.values.padding.left = parseInt(this.content.padding_left.val(), 10);
        this.values.merge_descriptions = this.content.merge_descriptions.prop('checked');
        this.values.merge_aggressive = this.content.merge_aggressive.prop('checked');
        this.values.merge_until = parseInt(this.content.merge_until.val(), 10) || 0;
        this.values.text_background = this.content.text_background.prop('checked');
        this.values.text_background_color = this.content.text_background_color.val();
    }

    update_merge_until(){
        this.content.merge_until
          .html(this.data_pivot._get_description_options())
          .val(this.values.merge_until);
    }
}


export {_DataPivot_settings_refline};
export {_DataPivot_settings_refrect};
export {_DataPivot_settings_label};
export {_DataPivot_settings_sorts};
export {_DataPivot_settings_filters};
export {_DataPivot_settings_spacers};
export {_DataPivot_settings_description};
export {_DataPivot_settings_pointdata};
export {_DataPivot_settings_conditionalFormat};
export {_DataPivot_ColorGradientSVG};
export {_DataPivot_settings_conditional};
export {_DataPivot_settings_linedata};
export {_DataPivot_settings_general};
