import $ from "$";

import StyleViewer from "./StyleViewer";
import {StyleSymbol, StyleLine, StyleText, StyleRectangle} from "./Styles";
import {NULL_CASE} from "./shared";
import HAWCModal from "utils/HAWCModal";

class StyleManager {
    constructor(pivot) {
        this.pivot = pivot;
        this.styles = {symbols: [], lines: [], texts: [], rectangles: []};
        this.selects = {symbols: [], lines: [], texts: [], rectangles: []};
        this.se = {};
        this.modal = new HAWCModal();

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
        var select = $('<select class="form-control">').html(this._build_options(style_type));
        if (include_null) {
            select.prepend(`<option value="${NULL_CASE}">${NULL_CASE}</option>`);
        }
        if (selected_style) {
            select.find(`option[value="${selected_style}"]`).prop("selected", true);
        }
        this.selects[style_type].push(select);
        return select;
    }

    update_selects(style_type) {
        for (var i = 0; i < this.selects[style_type].length; i++) {
            var select = this.selects[style_type][i],
                sel = select.find("option:selected").val();
            select.html(this._build_options(style_type));
            select.find(`option[value="${sel}"]`).prop("selected", true);
        }
    }

    _build_options(style_type) {
        var options = [];
        this.styles[style_type].forEach(function(v) {
            options.push(
                $(`<option value="${v.settings.name}">${v.settings.name}</option>`).data("d", v)
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
            container = $('<div class="container-fluid">'),
            style_div = $('<div class="row">'),
            form_div = $('<div class="col-md-6">'),
            vis_div = $('<div class="col-md-6">'),
            d3_div = $("<div>"),
            button_well = $('<div class="well">'),
            saveSettings = $(
                '<button type="button" class="btn btn-primary">Save and close</button>'
            ),
            title = $(`<h3>${toTitleCase(style_type)}</h3>`),
            modalHeader = $(`<h3>${toTitleCase(style_type)}</h3>`),
            modalBody = $('<div class="style_fields">'),
            modalFooter = saveSettings;

        // functionality
        var get_style = function() {
                return style_selector.find("option:selected").data("d");
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
                    case "symbols":
                        Cls = StyleSymbol;
                        break;
                    case "lines":
                        Cls = StyleLine;
                        break;
                    case "texts":
                        Cls = StyleText;
                        break;
                    case "rectangles":
                        Cls = StyleRectangle;
                        break;
                }
                var style = new Cls(self, undefined, true);
                self.modal.show({}, cb => style.draw_modal(self.modal.$modalDiv));
            },
            edit_style = function() {
                var style = get_style();
                self.modal.show({}, cb => style.draw_modal(self.modal.$modalDiv));
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
            save_style = function(e) {
                e.preventDefault();
                var style = self.modal.$modalDiv.data("d");
                if (self.save_settings(style, style_type)) {
                    self.update_selects(style_type);
                    style_selector
                        .find(`option[value="${style.settings.name}"]`)
                        .prop("selected", true);
                    load_style(); // update selector outside modal
                    self.modal.$modalDiv.modal("hide");
                }
            };

        // create buttons and event-bindings
        var style_selector = this.add_select(style_type).on("change", load_style),
            button_new_style = $(
                '<button style="margin-right:5px" class="btn btn-primary"><i class="fa fa-plus"></i> New</button>'
            ).click(new_style),
            button_edit_style = $(
                '<button style="margin-right:5px" class="btn btn-info"><i class="fa fa-pencil-square-o"></i> Update</button>'
            ).click(edit_style),
            button_delete_style = $(
                '<button style="margin-right:5<p></p>px" class="btn btn-danger"><i class="fa fa-trash"></i> Delete</button>'
            ).click(delete_style);

        saveSettings.on("click", save_style);

        // put all the pieces together
        form_div.append(style_selector, button_well);
        button_well.append(button_new_style, button_edit_style, button_delete_style);
        style_div.append(form_div, vis_div.append(d3_div));
        container.append(title, style_div, this.modal);

        // load with initial style
        load_style();

        // load containers w/ event bindings
        this.modal
            .addHeader(modalHeader)
            .addBody(modalBody)
            .addFooter(modalFooter);

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

        if (style_object.isNew && !isNameUnique(style_type, new_styles.name, style_object)) {
            alert("Error - style name must be unique!");
            return false;
        }

        for (var field in new_styles) {
            // eslint-disable-next-line no-prototype-builtins
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
