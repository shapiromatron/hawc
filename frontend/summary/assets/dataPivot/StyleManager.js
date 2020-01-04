import $ from '$';

import StyleViewer from './StyleViewer';
import { StyleSymbol, StyleLine, StyleText, StyleRectangle } from './Styles';
import { NULL_CASE } from './shared';

class StyleManager {
    constructor(pivot) {
        this.pivot = pivot;
        this.styles = { symbols: [], lines: [], texts: [], rectangles: [] };
        this.selects = { symbols: [], lines: [], texts: [], rectangles: [] };
        this.se = {};

        //unpack styles
        var self = this;
        this.pivot.settings.styles.symbols.forEach(function(v) {
            self.styles.symbols.push(new StyleSymbol(self, v, false));
        });
        this.pivot.settings.styles.lines.forEach(function(v) {
            self.styles.lines.push(new StyleLine(self, v, false));
        });
        this.pivot.settings.styles.texts.forEach(function(v) {
            self.styles.texts.push(new StyleText(self, v, false));
        });
        this.pivot.settings.styles.rectangles.forEach(function(v) {
            self.styles.rectangles.push(new StyleRectangle(self, v, false));
        });
    }

    add_select(style_type, selected_style, include_null) {
        var select = $('<select class="span12">').html(this._build_options(style_type));
        if (include_null) {
            select.prepend(`<option value="${NULL_CASE}">${NULL_CASE}</option>`);
        }
        if (selected_style) {
            select.find(`option[value="${selected_style}"]`).prop('selected', true);
        }
        this.selects[style_type].push(select);
        return select;
    }

    update_selects(style_type) {
        for (var i = 0; i < this.selects[style_type].length; i++) {
            var select = this.selects[style_type][i],
                sel = select.find('option:selected').val();
            select.html(this._build_options(style_type));
            select.find('option[value="{0}"]'.printf(sel)).prop('selected', true);
        }
    }

    _build_options(style_type) {
        var options = [];
        this.styles[style_type].forEach(function(v) {
            options.push(
                $('<option value="{0}">{0}</option>'.printf(v.settings.name)).data('d', v)
            );
        });
        return options;
    }

    build_styles_crud(style_type) {
        // components
        var self = this,
            toTitleCase = function(str) {
                return str.replace(/\w\S*/g, function(word) {
                    return word.charAt(0).toUpperCase() + word.substr(1).toLowerCase();
                });
            },
            container = $('<div class="row-fluid">'),
            title = $(`<h3>${toTitleCase(style_type)}</h3>`),
            style_div = $('<div class="row-fluid">'),
            form_div = $('<div class="span6">'),
            vis_div = $('<div class="span6">'),
            d3_div = $('<div>'),
            modal = $(
                '<div class="modal hide fade">' +
                    '<div class="modal-header">' +
                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
                    '<h3></h3>' +
                    '</div>' +
                    '<div class="modal-body">' +
                    '<div class="style_fields"></div>' +
                    '</div>' +
                    '<div class="modal-footer">' +
                    '<a href="#" class="btn" data-dismiss="modal" aria-hidden="true">Close</a>' +
                    '</div>' +
                    '</div>'
            ),
            button_well = $('<div class="well">');

        // functionality
        var get_style = function() {
                return style_selector.find('option:selected').data('d');
            },
            load_style = function() {
                // load style into details portion of Styles tab
                var style = get_style();
                if (!self.se[style_type]) {
                    self.se[style_type] = new StyleViewer(d3_div, style);
                } else {
                    self.se[style_type].update_style_object(style);
                }
            },
            new_style = function() {
                var Cls;
                switch (style_type) {
                    case 'symbols':
                        Cls = StyleSymbol;
                        break;
                    case 'lines':
                        Cls = StyleLine;
                        break;
                    case 'texts':
                        Cls = StyleText;
                        break;
                    case 'rectangles':
                        Cls = StyleRectangle;
                        break;
                }
                var style = new Cls(self, undefined, true);
                modal.modal('show');
                style.draw_modal(modal);
            },
            edit_style = function() {
                var style = get_style();
                modal.modal('show');
                style.draw_modal(modal);
            },
            delete_style = function() {
                var style = get_style(),
                    i;

                // remove from settings
                for (i = 0; i < self.pivot.settings.styles[style_type].length; i++) {
                    if (self.pivot.settings.styles[style_type][i] === style.settings) {
                        self.pivot.settings.styles[style_type].splice(i, 1);
                        break;
                    }
                }

                // remove from style objects
                for (i = 0; i < self.styles[style_type].length; i++) {
                    if (self.styles[style_type][i] === style) {
                        self.styles[style_type].splice(i, 1);
                        break;
                    }
                }

                // load next available style and update selects
                load_style();
                self.update_selects(style_type);
            },
            save_style = function() {
                var style = modal.data('d');
                if (self.save_settings(style, style_type)) {
                    self.update_selects(style_type);
                    style_selector
                        .find('option[value="{0}"]'.printf(style.settings.name))
                        .prop('selected', true);
                    modal.modal('hide');
                }
            };

        // create buttons and event-bindings
        var style_selector = this.add_select(style_type).on('change', load_style),
            button_new_style = $(
                '<button style="margin-right:5px" class="btn btn-primary"><i class="fa fa-plus"></i> New</button>'
            ).click(new_style),
            button_edit_style = $(
                '<button style="margin-right:5px" class="btn btn-info"><i class="fa fa-pencil-square-o"></i> Update</button>'
            ).click(edit_style),
            button_delete_style = $(
                '<button style="margin-right:5<p></p>px" class="btn btn-danger"><i class="fa fa-trash"></i> Delete</button>'
            ).click(delete_style);

        modal
            .find('.modal-footer')
            .prepend($('<a href="#" class="btn btn-primary">Save and close</a>').click(save_style));
        modal.on('hidden', load_style);

        // put all the pieces together
        form_div.append(style_selector, button_well);
        button_well.append(button_new_style, button_edit_style, button_delete_style);
        style_div.append(form_div, vis_div.append(d3_div));
        container.append(title, style_div, modal);

        load_style(); // load with initial style

        return container;
    }

    save_settings(style_object, style_type) {
        var self = this,
            new_styles = style_object.get_modified_settings(),
            isNameUnique = function(style_type, name, style_object) {
                var unique = true;
                self.styles[style_type].forEach(function(v) {
                    if (v.settings.name === name && v !== style_object) {
                        unique = false;
                    }
                });
                return unique;
            };

        if (!isNameUnique(style_type, new_styles.name, style_object)) {
            alert('Error - style name must be unique!');
            return false;
        }

        for (var field in new_styles) {
            if (style_object.settings.hasOwnProperty(field)) {
                style_object.settings[field] = new_styles[field];
            }
        }

        if (style_object.isNew) {
            style_object.isNew = false;
            this.styles[style_type].push(style_object);
            this.pivot.settings.styles[style_type].push(style_object.settings);
        }

        return true;
    }
}

export default StyleManager;
