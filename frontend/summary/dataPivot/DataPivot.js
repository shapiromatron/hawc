import * as d3 from "d3";
import _ from "lodash";
import React from "react";
import {createRoot} from "react-dom/client";
import DataTable from "shared/components/DataTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import $ from "$";

import {getInteractivityOptions} from "../interactivity/actions";
import {handleVisualError} from "../summary/common";
import ColumnSelectManager from "./components/ColumnNameSelect";
import DataPivotDefaultSettings from "./DataPivotDefaultSettings";
import DataPivotVisualization from "./DataPivotVisualization";
import build_data_tab from "./DPFDataTab";
import build_description_tab from "./DPFDescriptionTab";
import build_settings_general_tab from "./DPFGeneralSettingsTab";
import build_ordering_tab from "./DPFOrderTab";
import build_reference_tab from "./DPFReferenceTab";
import build_styles_tab from "./DPFStyleTab";
import StyleManager from "./StyleManager";
import Store from "./store";

class DataPivot {
    constructor(data, settings, dom_bindings, title, url) {
        if (_.keys(settings).length == 0) {
            settings = DataPivot.default_plot_settings();
        }
        this.settings = settings;
        this.raw_data = data;
        this.title = title;
        this.url = url;
        this.onRendered = [];
        this.processDataset();
        if (dom_bindings.update) {
            this.build_edit_settings(dom_bindings);
        }
    }

    processDataset() {
        this.data = DataPivotVisualization.processDataset(this.raw_data, this.settings);
    }

    static get_object(pk, callback) {
        const url = `/summary/api/visual/${pk}/`,
            handleError = err => {
                $("#loading_div").hide();
                handleVisualError(err, $("#dp_display"));
            };

        fetch(url, h.fetchGet)
            .then(d => d.json())
            .then(d => {
                fetch(d.data_url + "?format=tsv", h.fetchGet)
                    .then(resp => {
                        if (!resp.ok) {
                            throw Error(`Invalid server response: ${resp.status}`);
                        }
                        return resp;
                    })
                    .then(d => d.text())
                    .then(data => d3.tsvParse(data))
                    .then(data => {
                        const dp = new DataPivot(data, d.settings, {}, d.title, d.url);
                        if (callback) {
                            callback(dp);
                        }
                    })
                    .catch(handleError);
            })
            .catch(handleError);
    }

    static displayAsModal(id) {
        DataPivot.get_object(id, d => d.displayAsModal());
    }

    static displayInline(id, setTitle, setBody) {
        DataPivot.get_object(id, obj => {
            var title = $("<h4>").html(obj.object_hyperlink()),
                content = $("<div>");

            setTitle(title);
            setBody(content);
            obj.build_data_pivot_vis(content);
        });
    }

    static displayEditView(data_url, settings, options) {
        fetch(data_url, h.fetchGet)
            .then(d => d.text())
            .then(data => d3.tsvParse(data))
            .then(data => {
                $("#loading_div").fadeOut();
                const dp = new DataPivot(data, settings, {
                    update: true,
                    container: options.container,
                    data_div: options.dataDiv,
                    settings_div: options.settingsDiv,
                    display_div: options.displayDiv,
                });

                $(options.submissionDiv).submit(function () {
                    $(options.settingsField).val(dp.get_settings_json());
                    return true;
                });
            })
            .catch(err => handleVisualError(err, null));
    }

    static default_plot_settings() {
        return DataPivotDefaultSettings;
    }

    static move_row(arr, obj, moveUp) {
        // class-level function; used to delete a settings input row
        var swap = function (arr, a, b) {
                if (a < 0 || b < 0) return;
                if (a >= arr.length || b >= arr.length) return;
                arr[a] = arr.splice(b, 1, arr[a])[0];
            },
            idx = arr.indexOf(obj.values);

        if (moveUp) {
            obj.tr.insertBefore(obj.tr.prev());
            swap(arr, idx, idx - 1);
        } else {
            obj.tr.insertAfter(obj.tr.next());
            swap(arr, idx, idx + 1);
        }
    }

    static delete_row(arr, obj) {
        // class-level function; used to delete a settings input row
        obj.tr.remove();
        arr.splice(arr.indexOf(obj.values), 1);
    }

    static build_movement_td(arr, self, options) {
        //build a td including buttons for movement
        var td = $("<td>"),
            up = $(
                '<button class="btn btn-info btn-sm" title="move up"><i class="fa fa-arrow-up"></button>'
            ).on("click", function () {
                DataPivot.move_row(arr, self, true);
            }),
            down = $(
                '<button class="btn btn-info btn-sm mx-1" title="move down"><i class="fa fa-arrow-down"></button>'
            ).on("click", function () {
                DataPivot.move_row(arr, self, false);
            }),
            del = $(
                '<button class="btn btn-danger btn-sm" title="remove"><i class="fa fa-trash"></button>'
            ).on("click", function () {
                DataPivot.delete_row(arr, self);
            });

        if (options.showSort) td.append(up, down);
        td.append(del);
        return td;
    }

    static getRowDetails(values) {
        var unique_tokens = _.chain(values)
                .uniq()
                .map(_.toString) // cast all discrete token values to strings
                .without("")
                .sort()
                .value(),
            numeric = values.filter(v => $.isNumeric(v)),
            range = numeric.length > 0 ? d3.extent(numeric) : undefined;

        return {
            unique_tokens,
            numeric,
            range,
        };
    }

    static rangeInputDiv(input) {
        // given an numeric-range input, return a div containing input and text
        // field which updates based on current value.
        const currentValue = $('<div class="input-group-text">').text(input.val());
        input.on("change", () => currentValue.text(input.val()));
        return $('<div class="input-group">')
            .append(input)
            .append($('<div class="input-group-append pl-3">').append(currentValue));
    }

    build_edit_settings(dom_bindings) {
        var self = this,
            editable = true;
        this.store = new Store(this);
        this.style_manager = new StyleManager(this);
        this.column_select_manager = new ColumnSelectManager(this);
        this.$div = $(dom_bindings.container);
        this.$data_div = $(dom_bindings.data_div);
        this.$settings_div = $(dom_bindings.settings_div);
        this.$display_div = $(dom_bindings.display_div);

        // rebuild visualization whenever selected
        $('a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
            if (self.$display_div[0] === $($(e.target).attr("href"))[0]) {
                self.build_data_pivot_vis(self.$display_div, editable);
            }
        });

        this.build_data_table();
        this.build_settings();
        this.$div.fadeIn();
    }

    build_data_pivot_vis($div, editable) {
        try {
            delete this.plot;
            editable = editable || false;
            this.plot = new DataPivotVisualization(
                _.cloneDeep(this.raw_data),
                this.settings,
                $div,
                editable
            );
        } catch (err) {
            handleVisualError(err, $div);
        }
    }

    build_data_table() {
        const root = createRoot(this.$data_div[0]);
        root.render(<DataTable dataset={this.data} />);
    }

    addOnRenderedCallback(cb) {
        this.onRendered.push(cb);
    }

    triggerOnRenderedCallbacks() {
        this.onRendered.forEach(cb => cb());
    }

    build_settings() {
        const headers = _.keys(this.data[0]);
        this.interactivity_options = getInteractivityOptions(headers)
            .map(d => `<option value="${d.id}">${d.label}</option>`)
            .join("");

        var self = this,
            content = [
                $('<ul class="nav nav-tabs">').append(
                    '<li class="nav-item"><a class="nav-link active" href="#data_pivot_settings_description" data-toggle="tab">Descriptive text columns</a></li>',
                    '<li class="nav-item"><a class="nav-link" href="#data_pivot_settings_data" data-toggle="tab">Visualization data</a></li>',
                    '<li class="nav-item"><a class="nav-link dp_ordering_tab" href="#data_pivot_settings_ordering" data-toggle="tab">Data filtering and ordering</a></li>',
                    '<li class="nav-item"><a class="nav-link" href="#data_pivot_settings_ref" data-toggle="tab">References</a></li>',
                    '<li class="nav-item"><a class="nav-link" href="#data_pivot_settings_styles" data-toggle="tab">Styles</a></li>',
                    '<li class="nav-item"><a class="nav-link dp_general_tab" href="#data_pivot_settings_general" data-toggle="tab">Other settings</a></li>'
                ),
                $('<div class="tab-content"></div>').append(
                    build_description_tab(self),
                    build_data_tab(self),
                    build_ordering_tab(self),
                    build_reference_tab(self),
                    build_styles_tab(self),
                    build_settings_general_tab(self)
                ),
            ];

        this.$settings_div.html(content).on("shown.bs.tab", function (e) {
            if ($(e.target).attr("href") === "#data_pivot_settings_general") {
                self._dp_settings_general.update_merge_until();
            }
            self.triggerOnRenderedCallbacks();
        });
    }

    _get_description_options() {
        return this.settings.description_settings.map(
            (d, i) => `<option value="${i}">${d.header_name}</option>`
        );
    }

    get_settings_json() {
        return JSON.stringify(this.settings);
    }

    displayAsModal() {
        var self = this,
            modal = new HAWCModal(),
            title = `<h4>${this.title}</h4>`,
            $plot = $('<div class="col-md-12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row">').append($plot)
            );

        modal.getModal().on("shown.bs.modal", () => self.build_data_pivot_vis($plot));

        modal
            .addHeader([title, HAWCUtils.unpublished(this.data.published, window.isEditable)])
            .addBody($content)
            .addFooter("")
            .show();
    }

    object_hyperlink() {
        return $("<a>").attr("href", this.url).attr("target", "_blank").text(this.title);
    }
}

export default DataPivot;
