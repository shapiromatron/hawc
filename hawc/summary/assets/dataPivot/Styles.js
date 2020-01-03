import $ from '$';

import DataPivot from './DataPivot';
import StyleViewer from './StyleViewer';

class StyleSymbol {
    constructor(style_manager, settings, isNew) {
        this.type = 'symbol';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleSymbol.default_settings();
        return this;
    }

    static default_settings() {
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

    draw_modal($modal) {
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal
            .find('.style_fields input[type="color"]')
            .spectrum({ showInitial: true, showInput: true });
        $modal.data('d', this);
    }

    get_modified_settings() {
        var settings = {},
            fields = ['name', 'size', 'fill', 'fill-opacity', 'stroke', 'stroke-width'];
        for (var i = 0; i < fields.length; i++) {
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings.type = this.$modal.find('select[name="type"] option:selected').val();
        return settings;
    }

    _draw_setting_controls() {
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj) {
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append($('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function() {
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">')
            .val(set.name)
            .change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function() {
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //size
        form.append(
            add_horizontal_field(
                'Size',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="size" type="range" min="0" max="500" step="5" value="{0}">'.printf(
                            set.size
                        )
                    )
                )
            )
        );

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
        form.append(
            add_horizontal_field(
                'Fill',
                $('<input name="fill" type="color" value="{0}">'.printf(set.fill))
            )
        );

        //fill-opacity
        form.append(
            add_horizontal_field(
                'Fill-opacity',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="fill-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'.printf(
                            set['fill-opacity']
                        )
                    )
                )
            )
        );

        //stroke
        form.append(
            add_horizontal_field(
                'Stroke',
                $('<input name="stroke" type="color" value="{0}">'.printf(set.stroke))
            )
        );

        //stroke-width
        form.append(
            add_horizontal_field(
                'Stroke-width',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'.printf(
                            set['stroke-width']
                        )
                    )
                )
            )
        );

        this.controls = form;
    }
}

class StyleText {
    constructor(style_manager, settings, isNew) {
        this.type = 'text';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleText.default_settings();
        return this;
    }

    static default_settings() {
        return {
            name: 'base',
            fill: '#000',
            rotate: '0',
            'font-size': '12px',
            'font-weight': 'normal',
            'text-anchor': 'start',
            'fill-opacity': 1,
        };
    }

    static default_header() {
        return {
            name: 'header',
            fill: '#000',
            rotate: '0',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-anchor': 'middle',
            'fill-opacity': 1,
        };
    }

    static default_title() {
        return {
            name: 'title',
            fill: '#000',
            rotate: '0',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-anchor': 'middle',
            'fill-opacity': 1,
        };
    }

    draw_modal($modal) {
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal
            .find('.style_fields input[type="color"]')
            .spectrum({ showInitial: true, showInput: true });
        $modal.data('d', this);
    }

    get_modified_settings() {
        var settings = {},
            fields = ['name', 'font-size', 'fill', 'fill-opacity', 'rotate'];
        for (var i = 0; i < fields.length; i++) {
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings['font-size'] = settings['font-size'] + 'px';
        settings['text-anchor'] = this.$modal
            .find('select[name="text-anchor"] option:selected')
            .val();
        settings['font-weight'] = this.$modal
            .find('select[name="font-weight"] option:selected')
            .val();
        return settings;
    }

    _draw_setting_controls() {
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj) {
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append($('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function() {
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">')
            .val(set.name)
            .change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function() {
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //size
        form.append(
            add_horizontal_field(
                'Font Size',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="font-size" type="range" min="8" max="20" step="1" value="{0}">'.printf(
                            parseInt(set['font-size'], 10)
                        )
                    )
                )
            )
        );

        //fill
        form.append(
            add_horizontal_field(
                'Fill',
                $('<input name="fill" type="color" value="{0}">'.printf(set.fill))
            )
        );

        //fill opacity
        form.append(
            add_horizontal_field(
                'Fill opacity',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="fill-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'.printf(
                            set['fill-opacity']
                        )
                    )
                )
            )
        );

        //text-anchor
        var text_anchor = $('<select name="text-anchor"></select>').html([
            '<option value="start">start</option>',
            '<option value="middle">middle</option>',
            '<option value="end">end</option>',
        ]);
        text_anchor.find('option[value="{0}"]'.printf(set['text-anchor'])).prop('selected', true);
        form.append(add_horizontal_field('Type', text_anchor));

        //text-anchor
        var font_weight = $('<select name="font-weight"></select>').html([
            '<option value="normal">normal</option>',
            '<option value="bold">bold</option>',
        ]);
        font_weight.find('option[value="{0}"]'.printf(set['font-weight'])).prop('selected', true);
        form.append(add_horizontal_field('Type', font_weight));

        //rotate
        form.append(
            add_horizontal_field(
                'Rotation',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="rotate" type="range" min="0" max="360" step="15" value="{0}">'.printf(
                            set.rotate
                        )
                    )
                )
            )
        );

        this.controls = form;
    }
}

class StyleLine {
    constructor(style_manager, settings, isNew) {
        this.type = 'line';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleLine.default_settings();
        return this;
    }

    static default_settings() {
        return {
            name: 'base',
            stroke: '#708090',
            'stroke-dasharray': 'none',
            'stroke-opacity': 0.9,
            'stroke-width': 3,
        };
    }

    static default_reference_line() {
        return {
            name: 'reference line',
            stroke: '#000000',
            'stroke-dasharray': 'none',
            'stroke-opacity': 0.8,
            'stroke-width': 2,
        };
    }

    draw_modal($modal) {
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal
            .find('.style_fields input[type="color"]')
            .spectrum({ showInitial: true, showInput: true });
        $modal.data('d', this);
    }

    get_modified_settings() {
        var settings = {},
            fields = ['name', 'stroke', 'stroke-width', 'stroke-opacity'];
        for (var i = 0; i < fields.length; i++) {
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        settings['stroke-dasharray'] = this.$modal
            .find('select[name="stroke-dasharray"] option:selected')
            .val();
        return settings;
    }

    _draw_setting_controls() {
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj) {
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append($('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function() {
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">')
            .val(set.name)
            .change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function() {
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //stroke
        form.append(
            add_horizontal_field(
                'Stroke',
                $('<input name="stroke" type="color" value="{0}">'.printf(set.stroke))
            )
        );

        //stroke-width
        form.append(
            add_horizontal_field(
                'Stroke-width',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'.printf(
                            set['stroke-width']
                        )
                    )
                )
            )
        );

        //stroke-opacity
        form.append(
            add_horizontal_field(
                'Stroke-opacity',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="stroke-opacity" type="range" min="0" max="1" step="0.05" value="{0}">'.printf(
                            set['stroke-opacity']
                        )
                    )
                )
            )
        );

        //line-style
        var line_style = $('<select name="stroke-dasharray"></select>').html([
            '<option value="none">solid</option>',
            '<option value="10, 10">dashed</option>',
            '<option value="2, 3">dotted</option>',
            '<option value="15, 10, 5, 10">dash-dotted</option>',
        ]);
        line_style
            .find('option[value="{0}"]'.printf(set['stroke-dasharray']))
            .prop('selected', true);
        form.append(add_horizontal_field('Line style', line_style));

        this.controls = form;
    }
}

class StyleRectangle {
    constructor(style_manager, settings, isNew) {
        this.type = 'rectangle';
        this.isNew = isNew;
        this.style_manager = style_manager;
        this.settings = settings || StyleRectangle.default_settings();
        return this;
    }

    static default_settings() {
        return {
            name: 'base',
            fill: '#999999',
            stroke: '#000000',
            'fill-opacity': 0.8,
            'stroke-width': 1.0,
        };
    }

    draw_modal($modal) {
        this.$modal = $modal;
        this._draw_setting_controls();
        this.$modal.find('.style_fields').html(this.controls);
        this.$modal
            .find('.style_fields input[type="color"]')
            .spectrum({ showInitial: true, showInput: true });
        $modal.data('d', this);
    }

    get_modified_settings() {
        var settings = {},
            fields = ['name', 'fill', 'fill-opacity', 'stroke', 'stroke-width'];
        for (var i = 0; i < fields.length; i++) {
            settings[fields[i]] = this.$modal.find('input[name="{0}"]'.printf(fields[i])).val();
        }
        return settings;
    }

    _draw_setting_controls() {
        var form = $('<form class="form-horizontal"></form>'),
            set = this.settings,
            add_horizontal_field = function(label_text, html_obj) {
                return $('<div class="control-group"></div>')
                    .append('<label class="control-label">{0}</label>'.printf(label_text))
                    .append($('<div class="controls"></div>').append(html_obj));
            },
            image_div = $('<div></div>'),
            sv = new StyleViewer(image_div, this),
            self = this;

        //image
        form.append(image_div).on('change', 'input,select', function() {
            sv.apply_new_styles(self.get_modified_settings(), true);
        });

        //name
        var name_field = $('<input name="name" type="text">')
            .val(set.name)
            .change(update_title);
        form.append(add_horizontal_field('Name', name_field));
        var update_title = function() {
            self.$modal.find('.modal-header h3').html(name_field.val());
        };
        update_title();

        //fill
        form.append(
            add_horizontal_field(
                'Fill',
                $('<input name="fill" type="color" value="{0}">'.printf(set.fill))
            )
        );

        //fill-opacity
        form.append(
            add_horizontal_field(
                'Fill-opacity',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="fill-opacity" type="range" min="0" max="1" step="0.1" value="{0}">'.printf(
                            set['fill-opacity']
                        )
                    )
                )
            )
        );

        //stroke
        form.append(
            add_horizontal_field(
                'Stroke',
                $('<input name="stroke" type="color" value="{0}">'.printf(set.stroke))
            )
        );

        //stroke-width
        form.append(
            add_horizontal_field(
                'Stroke-width',
                DataPivot.rangeInputDiv(
                    $(
                        '<input name="stroke-width" type="range" min="0" max="10" step="0.5" value="{0}">'.printf(
                            set['stroke-width']
                        )
                    )
                )
            )
        );

        this.controls = form;
    }
}

export { StyleSymbol };
export { StyleText };
export { StyleLine };
export { StyleRectangle };
