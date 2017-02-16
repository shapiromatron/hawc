import $ from '$';
import d3 from 'd3';

import {_DataPivot_settings_conditionalFormat} from './ConditionalFormat';
import DataPivot from './DataPivot';
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
            .append($('<td>').append('<b>Low range:</b><br>',
                                          this.content.low_field_name,
                                          '<br><b>High range:</b><br>',
                                          this.content.high_field_name))
            .append($('<td>').append(this.content.header_name))
            .append($('<td>').append(this.content.marker_style))
            .on('change', 'input,select', function(v){
                self.data_push();

                // update legend
                var obj = {
                    line_index: index,
                    label: self.content.header_name.val(),
                    line_style: self.content.marker_style.find('option:selected').text(),
                };
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

let buildHeaderTr = function(lst){
    return $('<tr>').html(lst.map((v)=>`<th>${v}</th>`).join());
};


export {_DataPivot_settings_refline};
export {_DataPivot_settings_refrect};
export {_DataPivot_settings_label};
export {_DataPivot_settings_sorts};
export {_DataPivot_settings_filters};
export {_DataPivot_settings_spacers};
export {_DataPivot_settings_description};
export {_DataPivot_settings_pointdata};
export {_DataPivot_settings_linedata};
export {_DataPivot_settings_general};
export {buildHeaderTr};
