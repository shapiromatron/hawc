import $ from '$';
import d3 from 'd3';

import D3Plot from 'utils/D3Plot';

import DataPivot from './DataPivot';


class StyleSymbol {

    constructor(style_manager, settings, isNew){
        this.type = 'symbol';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleSymbol.default_settings();
        return this;
    }

    static default_settings(){
        return {
            name: 'base',
            type: 'circle',
            size: 130,
            fill: '#000',
            'fill-opacity': 1.0,
            stroke: '#fff',
            'stroke-width': 1,
        };
    }

    draw_modal($modal){
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal.find('.style_fields input[type="color"]')
            .spectrum({showInitial: true, showInput: true});
        $modal.data('d', this);
    }

    get_modified_settings(){
        var settings = {},
            fields = ['name', 'size', 'fill', 'fill-opacity', 'stroke', 'stroke-width'];
        for(var i=0; i<fields.length; i++){
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings.type = this.$modal.find('select[name="type"] option:selected').val();
        return settings;
    }

    _draw_setting_controls(){
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj){
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append( $('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function(){
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">').val(set.name).change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function(){
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //size
        form.append(add_horizontal_field('Size',
             DataPivot.rangeInputDiv($('<input name="size" type="range" min="0" max="500" step="5" value="{0}">'
                .printf(set.size)))));

        //type
        var type = $('<select name="type"></select>').html([
            '<option value="circle">circle</option>',
            '<option value="cross">cross</option>',
            '<option value="diamond">diamond</option>',
            '<option value="square">square</option>',
            '<option value="triangle-down">triangle-down</option>',
            '<option value="triangle-up">triangle-up</option>',
        ]);

        type.find('option[value="{0}"]'.printf(set.type)).prop('selected', true);
        form.append(add_horizontal_field('Type', type));

        //fill
        form.append(add_horizontal_field('Fill',
            $('<input name="fill" type="color" value="{0}">'
                .printf(set.fill))));

        //fill-opacity
        form.append(add_horizontal_field('Fill-opacity',
             DataPivot.rangeInputDiv($('<input name="fill-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'
                .printf(set['fill-opacity'])))));

        //stroke
        form.append(add_horizontal_field('Stroke',
            $('<input name="stroke" type="color" value="{0}">'
                .printf(set.stroke))));

        //stroke-width
        form.append(add_horizontal_field('Stroke-width',
             DataPivot.rangeInputDiv($('<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'
                .printf(set['stroke-width'])))));

        this.controls = form;
    }
}

class StyleText {

    constructor(style_manager, settings, isNew){
        this.type = 'text';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleText.default_settings();
        return this;
    }

    static default_settings(){
        return {
            name: 'base',
            fill: '#000',
            rotate : '0',
            'font-size': '12px',
            'font-weight': 'normal',
            'text-anchor': 'start',
            'fill-opacity': 1,
        };
    }

    static default_header(){
        return {
            name:'header',
            fill: '#000',
            rotate: '0',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-anchor': 'middle',
            'fill-opacity': 1,
        };
    }

    static default_title(){
        return {
            name: 'title',
            fill: '#000',
            rotate : '0',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-anchor': 'middle',
            'fill-opacity': 1,
        };
    }

    draw_modal($modal){
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal.find('.style_fields input[type="color"]')
            .spectrum({showInitial: true, showInput: true});
        $modal.data('d', this);
    }

    get_modified_settings(){
        var settings = {},
            fields = ['name', 'font-size', 'fill', 'fill-opacity', 'rotate'];
        for(var i=0; i<fields.length; i++){
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings['font-size'] = settings['font-size'] + 'px';
        settings['text-anchor'] = this.$modal.find('select[name="text-anchor"] option:selected').val();
        settings['font-weight'] = this.$modal.find('select[name="font-weight"] option:selected').val();
        return settings;
    }

    _draw_setting_controls(){
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj){
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append( $('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function(){
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">').val(set.name).change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function(){
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //size
        form.append(add_horizontal_field('Font Size',
             DataPivot.rangeInputDiv($('<input name="font-size" type="range" min="8" max="20" step="1" value="{0}">'
                .printf(parseInt(set['font-size'], 10))))));

        //fill
        form.append(add_horizontal_field('Fill',
            $('<input name="fill" type="color" value="{0}">'.printf(set.fill))));

        //fill opacity
        form.append(add_horizontal_field('Fill opacity',
             DataPivot.rangeInputDiv($('<input name="fill-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'.printf(set['fill-opacity'])))));

        //text-anchor
        var text_anchor = $('<select name="text-anchor"></select>')
            .html(['<option value="start">start</option>',
                   '<option value="middle">middle</option>',
                   '<option value="end">end</option>']);
        text_anchor.find('option[value="{0}"]'.printf(set['text-anchor'])).prop('selected', true);
        form.append(add_horizontal_field('Type', text_anchor));

        //text-anchor
        var font_weight = $('<select name="font-weight"></select>')
            .html(['<option value="normal">normal</option>',
                   '<option value="bold">bold</option>']);
        font_weight.find('option[value="{0}"]'.printf(set['font-weight'])).prop('selected', true);
        form.append(add_horizontal_field('Type', font_weight));

        //rotate
        form.append(add_horizontal_field('Rotation',
             DataPivot.rangeInputDiv($('<input name="rotate" type="range" min="0" max="360" step="15" value="{0}">'
                .printf(set.rotate)))));

        this.controls = form;
    }
}

class StyleLine {

    constructor(style_manager, settings, isNew){
        this.type = 'line';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleLine.default_settings();
        return this;
    }

    static default_settings(){
        return {
            name: 'base',
            stroke: '#708090',
            'stroke-dasharray': 'none',
            'stroke-opacity': 0.9,
            'stroke-width': 3,
        };
    }

    static default_reference_line(){
        return {
            name: 'reference line',
            stroke: '#000000',
            'stroke-dasharray': 'none',
            'stroke-opacity': 0.8,
            'stroke-width': 2,
        };
    }

    draw_modal($modal){
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal.find('.style_fields input[type="color"]')
            .spectrum({showInitial: true, showInput: true});
        $modal.data('d', this);
    }

    get_modified_settings(){
        var settings = {},
            fields = ['name', 'stroke', 'stroke-width', 'stroke-opacity'];
        for(var i=0; i<fields.length; i++){
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings['stroke-dasharray'] = this.$modal.find('select[name="stroke-dasharray"] option:selected').val();
        return settings;
    }

    _draw_setting_controls(){
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj){
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append( $('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function(){
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">').val(set.name).change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function(){
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //stroke
        form.append(add_horizontal_field('Stroke',
            $('<input name="stroke" type="color" value="{0}">'
                .printf(set.stroke))));

        //stroke-width
        form.append(add_horizontal_field('Stroke-width',
             DataPivot.rangeInputDiv($('<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'
              .printf(set['stroke-width'])))));

        //stroke-opacity
        form.append(add_horizontal_field('Stroke-opacity',
             DataPivot.rangeInputDiv($('<input name="stroke-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'
                .printf(set['stroke-opacity'])))));

        //line-style
        var line_style = $('<select name="stroke-dasharray"></select>')
            .html([
                '<option value="none">solid</option>',
                '<option value="10, 10">dashed</option>',
                '<option value="2, 3">dotted</option>',
                '<option value="15, 10, 5, 10">dash-dotted</option>']);
        line_style.find('option[value="{0}"]'.printf(set['stroke-dasharray'])).prop('selected', true);
        form.append(add_horizontal_field('Line style', line_style));

        this.controls = form;
    }
}

class StyleRectangle {

    constructor(style_manager, settings, isNew){
        this.type = 'rectangle';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleRectangle.default_settings();
        return this;
    }

    static default_settings(){
        return {
            name: 'base',
            fill: '#be6a62',
            stroke: '#be6a62',
            'fill-opacity': 0.3,
            'stroke-width': 1.5,
        };
    }

    draw_modal($modal){
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal.find('.style_fields input[type="color"]')
            .spectrum({showInitial: true, showInput: true});
        $modal.data('d', this);
    }

    get_modified_settings(){
        var settings = {},
            fields = ['name', 'fill', 'fill-opacity', 'stroke', 'stroke-width'];
        for(var i=0; i<fields.length; i++){
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        return settings;
    }

    _draw_setting_controls(){
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj){
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append( $('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function(){
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">').val(set.name).change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function(){
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //fill
        form.append(add_horizontal_field('Fill',
            $('<input name="fill" type="color" value="{0}">'
                .printf(set.fill))));

        //fill-opacity
        form.append(add_horizontal_field('Fill-opacity',
             DataPivot.rangeInputDiv($('<input name="fill-opacity" type="range" min="0" max="1" step="0.1" value="{0}">'
                .printf(set['fill-opacity'])))));

        //stroke
        form.append(add_horizontal_field('Stroke',
            $('<input name="stroke" type="color" value="{0}">'
                .printf(set.stroke))));

        //stroke-width
        form.append(add_horizontal_field('Stroke-width',
             DataPivot.rangeInputDiv($('<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'
                .printf(set['stroke-width'])))));

        this.controls = form;
    }
}

class StyleViewer extends D3Plot {

    constructor($plot_div, style, settings){
        super();
        this.style=style;
        this.settings = settings || StyleViewer.default_settings();
        this.set_defaults();
        this.plot_div = $plot_div;
        if(this.settings.plot_settings.build_plot_startup){this.build_plot();}
    }

    static default_settings(){
        return {
            plot_settings: {
                show_menu_bar: false,
                build_plot_startup: true,
                width: 50,
                height: 50,
                padding: {
                    top: 10,
                    right: 10,
                    bottom: 10,
                    left: 10,
                },
            },
        };
    }

    build_plot(){
        this.plot_div.html('');
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.draw_visualizations();
    }

    get_plot_sizes(){
        this.w = this.settings.plot_settings.width;
        this.h = this.settings.plot_settings.height;
        var menu_spacing = (this.settings.plot_settings.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom + menu_spacing) + 'px'});
    }

    set_defaults(){
        this.padding = $.extend({}, this.settings.plot_settings.padding); //copy object

        this.x_axis_settings = {
            domain: [0, 2],
            rangeRound: [0, this.settings.plot_settings.width],
            x_translate: 0,
            y_translate: 0,
            scale_type: 'linear',
            text_orient: 'bottom',
            axis_class: 'axis x_axis',
            gridlines: false,
            gridline_class: 'primary_gridlines x_gridlines',
            number_ticks: 10,
            axis_labels: false,
            label_format: undefined,
        };

        this.y_axis_settings = {
            domain: [0, 2],
            rangeRound: [0, this.settings.plot_settings.height],
            number_ticks: 10,
            x_translate: 0,
            y_translate: 0,
            scale_type: 'linear',
            text_orient: 'left',
            axis_class: 'axis y_axis',
            gridlines: false,
            gridline_class: 'primary_gridlines y_gridlines',
            axis_labels:false,
            label_format: undefined,
        };
    }

    draw_visualizations(){
        this.build_y_axis();
        this.build_x_axis();

        var self = this,
            x = this.x_scale,
            y = this.y_scale;

        if (this.style.type === 'line'){
            this.lines = this.vis.selectAll()
                .data([{x1: 0.25, x2: 1.75, y1: 1, y2: 1},
                       {x1: 0.25, x2: 0.25, y1: 0.5, y2: 1.5},
                       {x1: 1.75, x2: 1.75, y1: 0.5, y2: 1.5}])
                .enter().append('svg:line')
                    .attr('x1', (v) => x(v.x1))
                    .attr('x2', (v) => x(v.x2))
                    .attr('y1', (v) => y(v.y1))
                    .attr('y2', (v) => y(v.y2))
                .on('click', function(){self._update_styles(self.style.settings, true);});

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === 'rectangle'){
            this.rectangles = this.vis.selectAll()
                .data([{x: 0.25, y: 0.25, width: 1.5, height: 1.5}])
                .enter().append('svg:rect')
                    .attr('x', function(v){return x(v.x);})
                    .attr('y', function(v){return x(v.y);})
                    .attr('width', function(v){return y(v.width);})
                    .attr('height', function(v){return y(v.height);})
                .on('click', function(){self._update_styles(self.style.settings, true);});

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === 'symbol'){
            this.symbol = this.vis.selectAll('path')
                .data([
                    {x: 0.5, y: 0.5},
                    {x: 1.5, y: 0.5},
                    {x: 1.5, y: 1.5},
                    {x: 0.5, y: 1.5},
                ])
                .enter().append('path')
                    .attr('d', d3.svg.symbol())
                    .attr('transform', function(d) {
                        return 'translate(' + x(d.x) + ',' + y(d.y) + ')';
                    })
                    .on('click', function(){self._update_styles(self.style.settings, true);});

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === 'text'){
            this.lines = this.vis.selectAll()
                .data([
                    {x1: 1.25, x2: 0.75, y1: 1,    y2: 1},
                    {x1: 1,    x2: 1,    y1: 1.25, y2: 0.75},
                ])
                .enter()
                    .append('svg:line')
                    .attr('x1', function(v){return x(v.x1);})
                    .attr('x2', function(v){return x(v.x2);})
                    .attr('y1', function(v){return y(v.y1);})
                    .attr('y2', function(v){return y(v.y2);})
                    .attr('stroke-width', 2)
                    .attr('stroke', '#ccc');

            this.text = this.vis.append('svg:text')
                .attr('x', x(1))
                .attr('y', y(1))
                .text('text');

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type == 'legend'){
            if(this.settings.line_style) this.add_legend_lines();
            if(this.settings.line_style) this.add_legend_symbols();
            this._update_styles(this.style, false);
        }
    }

    add_legend_lines(){

        var x = this.x_scale,
            y = this.y_scale;

        this.lines = this.vis.selectAll()
            .data([
                {x1: 0.25, x2: 1.75, y1: 1, y2: 1},
                {x1: 0.25, x2: 0.25, y1: 0.5, y2: 1.5},
                {x1: 1.75, x2: 1.75, y1: 0.5, y2: 1.5}])
            .enter().append('svg:line')
                .attr('x1', function(v){return x(v.x1);})
                .attr('x2', function(v){return x(v.x2);})
                .attr('y1', function(v){return y(v.y1);})
                .attr('y2', function(v){return y(v.y2);});
    }

    add_legend_symbols(){

        var x = this.x_scale,
            y = this.y_scale;

        this.symbol = this.vis.selectAll('path')
            .data([{x: 1, y: 1}])
            .enter().append('path')
                .attr('d', d3.svg.symbol())
                .attr('transform', function(d) {return 'translate(' + x(d.x) + ',' + y(d.y) + ')'; });
    }

    _update_styles(style_settings, randomize_position){
        var x = this.x_scale,
            y = this.y_scale;

        if (this.style.type === 'line'){
            this.lines.transition()
                .duration(1000)
                .style(style_settings);
        }

        var randomize_data = function(){
            return [
                {x: Math.random()*2, y: Math.random()*2},
                {x: Math.random()*2, y: Math.random()*2},
                {x: Math.random()*2, y: Math.random()*2},
                {x: Math.random()*2, y: Math.random()*2}];
        };

        if (this.style.type === 'symbol'){

            var d = (randomize_position) ? randomize_data() : this.symbol.data();

            this.symbol
                .data(d)
                .transition()
                .duration(1000)
                .attr('transform', function(d) {return 'translate(' + x(d.x) + ',' + y(d.y) + ')'; })
                .attr('d', d3.svg.symbol()
                    .size(style_settings.size)
                    .type(style_settings.type))
                .style(style_settings);
        }

        if (this.style.type === 'text'){
            this.text.attr('transform', undefined);
            this.text
                .transition()
                .duration(1000)
                .attr('font-size', style_settings['font-size'])
                .attr('font-weight', style_settings['font-weight'])
                .attr('fill-opacity', style_settings['fill-opacity'])
                .attr('text-anchor', style_settings['text-anchor'])
                .attr('fill', style_settings.fill)
                .attr('transform', 'rotate({0} 25,25)'.printf(style_settings.rotate));
        }

        if (this.style.type === 'rectangle'){
            this.rectangles
                .transition()
                .duration(1000)
                .style(style_settings);
        }

        if (this.style.type === 'legend'){

            if(style_settings.line_style){
                if (!this.lines) this.add_legend_lines();
                this.lines.transition()
                    .duration(1000)
                    .style(style_settings.line_style.settings);
            } else {
                if (this.lines){
                    this.lines.remove();
                    delete this.lines;
                }
            }

            if(style_settings.symbol_style){
                if (!this.symbol) this.add_legend_symbols();
                this.symbol
                    .transition()
                    .duration(1000)
                    .attr('transform', function(d) {return 'translate(' + x(d.x) + ',' + y(d.y) + ')'; })
                    .attr('d', d3.svg.symbol()
                        .size(style_settings.symbol_style.settings.size)
                        .type(style_settings.symbol_style.settings.type))
                    .style(style_settings.symbol_style.settings);
            } else {
                if (this.symbol){
                    this.symbol.remove();
                    delete this.symbol;
                }
            }
        }
    }

    apply_new_styles(style_settings, randomize_position){
        // don't change the object, just the styles rendered in viewer
        this._update_styles(style_settings, randomize_position);
    }

    update_style_object(style){
        // change the style object
        this.style = style;
        this._update_styles(this.style.settings, true);
    }
}

export {StyleSymbol};
export {StyleText};
export {StyleLine};
export {StyleRectangle};
export {StyleViewer};
