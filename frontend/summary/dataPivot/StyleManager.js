import HAWCModal from "shared/utils/HAWCModal";
import $ from "$";

import StyleViewer from "./StyleViewer";
import {StyleLine, StyleRectangle, StyleSymbol, StyleText} from "./Styles";
import {NULL_CASE} from "./shared";

const _build_options = function (styles) {
        return styles.map(v =>
            $(`<option value="${v.settings.name}">${v.settings.name}</option>`).data("d", v)
        );
    },
    toTitleCase = function (str) {
        return str.replace(/\w\S*/g, function (word) {
            return word.charAt(0).toUpperCase() + word.substr(1).toLowerCase();
        });
    };

class StyleEditor {
    constructor(manager, styleType) {
        this.manager = manager;
        this.styleType = styleType;
        this.modal = new HAWCModal();
        this.viewer = null;
        this.container = null;
    }
    render() {
        var styleType = this.styleType,
            container = $("<div>"),
            style_div = $('<div class="row">'),
            form_div = $('<div class="col-md-6">'),
            vis_div = $('<div class="col-md-6">'),
            d3_div = $("<div>"),
            button_well = $('<div class="well">'),
            title = $(`<h3>${toTitleCase(styleType)}</h3>`),
            style_selector = this.manager.add_select(styleType),
            showModal = style => {
                const modalHeader = $(`<h3>${toTitleCase(styleType)}</h3>`),
                    modalBody = $('<div class="style_fields">'),
                    modalFooter = $(
                        '<button type="button" class="btn btn-primary">Save and close</button>'
                    ).on("click", save_style);

                this.modal
                    .addHeader(modalHeader)
                    .addBody(modalBody)
                    .addFooter(modalFooter)
                    .show({}, _cb => style.draw_modal(this.modal.$modalDiv));
            },
            get_style = () => style_selector.find("option:selected").data("d"),
            load_style = () => {
                // load style into details portion of Styles tab
                var style = get_style();
                if (this.viewer === null) {
                    this.viewer = new StyleViewer(d3_div, style);
                }
                this.viewer.update_style_object(style);
            },
            new_style = () => {
                var Cls;
                switch (styleType) {
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
                var style = new Cls(this, undefined, true);
                showModal(style);
            },
            edit_style = () => showModal(get_style()),
            delete_style = () => {
                var style = get_style();
                this.manager.delete_style(styleType, style);
                load_style();
            },
            save_style = e => {
                e.preventDefault();
                var style = this.modal.$modalDiv.data("d");
                if (this.manager.save_settings(style, styleType)) {
                    this.manager.update_selects(styleType);
                    style_selector
                        .find(`option[value="${style.settings.name}"]`)
                        .prop("selected", true);
                    load_style(); // update selector outside modal
                    this.modal.hide();
                }
            },
            button_new_style = $(
                '<button style="margin-right:5px" class="btn btn-primary"><i class="fa fa-plus"></i> New</button>'
            ).click(new_style),
            button_edit_style = $(
                '<button style="margin-right:5px" class="btn btn-info"><i class="fa fa-pencil-square-o"></i> Update</button>'
            ).click(edit_style),
            button_delete_style = $(
                '<button style="margin-right:5<p></p>px" class="btn btn-danger"><i class="fa fa-trash"></i> Delete</button>'
            ).click(delete_style);

        // put all the pieces together
        form_div.append(style_selector, button_well);
        button_well.append(button_new_style, button_edit_style, button_delete_style);
        style_div.append(form_div, vis_div.append(d3_div));
        container.append(title, style_div);

        // load initial style
        style_selector.on("change", load_style);
        load_style();

        this.container = container;
        return container;
    }
}

class StyleManager {
    constructor(pivot) {
        this.pivot = pivot;
        // build style objects
        this.styles = {
            symbols: this.pivot.settings.styles.symbols.map(v => new StyleSymbol(this, v, false)),
            lines: this.pivot.settings.styles.lines.map(v => new StyleLine(this, v, false)),
            texts: this.pivot.settings.styles.texts.map(v => new StyleText(this, v, false)),
            rectangles: this.pivot.settings.styles.rectangles.map(
                v => new StyleRectangle(this, v, false)
            ),
        };
        // placeholder for all selects in our data pivot which use these styles
        this.selects = {symbols: [], lines: [], texts: [], rectangles: []}; // all selects in data pivot
    }
    add_select(style_type, selected_style, include_null, opts) {
        // add a select box to select a style anywhere in the data pivot
        var styles = this.styles[style_type],
            select = $('<select class="form-control">').html(_build_options(styles));
        opts = opts || {null_label: NULL_CASE};
        if (include_null) {
            select.prepend(`<option value="${NULL_CASE}">${opts.null_label}</option>`);
        }
        if (selected_style) {
            select.find(`option[value="${selected_style}"]`).prop("selected", true);
        }
        this.selects[style_type].push(select);
        return select;
    }
    update_selects(style_type) {
        // if styles have changed, make sure updates are propagated
        for (var i = 0; i < this.selects[style_type].length; i++) {
            var select = this.selects[style_type][i],
                sel = select.find("option:selected").val(),
                styles = this.styles[style_type];
            select.html(_build_options(styles));
            select.find(`option[value="${sel}"]`).prop("selected", true);
        }
    }
    build_styles_crud(style_type) {
        // return container of the viewer
        const editor = new StyleEditor(this, style_type);
        return editor.render();
    }
    save_settings(style_object, style_type) {
        var self = this,
            new_styles = style_object.get_modified_settings(),
            isNameUnique = function (style_type, name, style_object) {
                var unique = true;
                self.styles[style_type].forEach(function (v) {
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
    delete_style = function (styleType, style) {
        var i,
            styles = this.styles[styleType],
            settingStyles = this.pivot.settings.styles[styleType];

        // remove from style objects
        for (i = 0; i < styles.length; i++) {
            if (styles[i] === style) {
                styles.splice(i, 1);
                break;
            }
        }

        // remove from settings
        for (i = 0; i < settingStyles.length; i++) {
            if (settingStyles[i] === style.settings) {
                settingStyles.splice(i, 1);
                break;
            }
        }

        // update selects
        this.update_selects(styleType);
    };
}

export default StyleManager;
