import $ from "$";
import * as d3 from "d3";

import {saveAs} from "filesaver.js";

import HAWCModal from "utils/HAWCModal";

import DataPivotDefaultSettings from "./DataPivotDefaultSettings";
import DataPivotExtension from "./DataPivotExtension";
import {NULL_CASE} from "./shared";
import StyleManager from "./StyleManager";

import build_description_tab from "./DPFDescriptionTab";
import build_settings_general_tab from "./DPFGeneralSettingsTab";
import build_data_tab from "./DPFDataTab";
import build_ordering_tab from "./DPFOrderTab";
import build_reference_tab from "./DPFReferenceTab";
import build_styles_tab from "./DPFStyleTab";

import DataPivotVisualization from "./DataPivotVisualization";

class DataPivot {
    constructor(data, settings, dom_bindings, title, url) {
        this.data = data;
        this.settings = settings || DataPivot.default_plot_settings();
        this.title = title;
        this.url = url;
        this.onRendered = [];
        if (dom_bindings.update) {
            this.build_edit_settings(dom_bindings);
        }
    }

    static get_object(pk, callback) {
        $.get(`/summary/api/data_pivot/${pk}/`, function(d) {
            d3.tsv(d.data_url, (row, idx) => DataPivot.massage_row(row, idx)).then(
                data => {
                    var dp = new DataPivot(data, d.settings, {}, d.title, d.url);
                    if (callback) {
                        callback(dp);
                    } else {
                        return dp;
                    }
                },
                error => {
                    console.error(error);
                    alert(`An error occurred; if the error continues please contact us.`);
                    throw "Server error";
                }
            );
        });
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
        d3.tsv(data_url, (d, i) => DataPivot.massage_row(d, i)).then(
            data => {
                $("#loading_div").fadeOut();
                const dp = new DataPivot(data, settings, {
                    update: true,
                    container: options.container,
                    data_div: options.dataDiv,
                    settings_div: options.settingsDiv,
                    display_div: options.displayDiv,
                });

                $(options.submissionDiv).submit(function() {
                    $(options.settingsField).val(dp.get_settings_json());
                    return true;
                });
            },
            error => {
                console.error(arguments);
                alert(`An error occurred; if the error continues please contact us.`);
                throw "Server error";
            }
        );
    }

    static default_plot_settings() {
        return DataPivotDefaultSettings;
    }

    static massage_row(row, i) {
        // make numbers in data numeric if possible
        // see https://github.com/mbostock/d3/wiki/CSV
        for (var field in row) {
            // eslint-disable-next-line no-prototype-builtins
            if (row.hasOwnProperty(field)) {
                row[field] = +row[field] || row[field];
            }
        }

        // add data-pivot row-level key and index
        row._dp_y = i;
        row._dp_pk = row["key"] || i;

        return row;
    }

    static move_row(arr, obj, moveUp) {
        // class-level function; used to delete a settings input row
        var swap = function(arr, a, b) {
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
                '<button class="btn btn-mini" title="move up"><i class="icon-arrow-up"></button>'
            ).on("click", function() {
                DataPivot.move_row(arr, self, true);
            }),
            down = $(
                '<button class="btn btn-mini" title="move down"><i class="icon-arrow-down"></button>'
            ).on("click", function() {
                DataPivot.move_row(arr, self, false);
            }),
            del = $(
                '<button class="btn btn-mini" title="remove"><i class="icon-remove"></button>'
            ).on("click", function() {
                DataPivot.delete_row(arr, self);
            });

        if (options.showSort) td.append(up, down);
        td.append(del);
        return td;
    }

    static getRowDetails(values) {
        var unique = d3.set(values),
            numeric = values.filter(v => $.isNumeric(v)),
            range = numeric.length > 0 ? d3.extent(numeric) : undefined;

        unique.remove("");
        unique.remove("undefined");

        return {
            unique: unique.values(),
            numeric,
            range,
        };
    }

    static rangeInputDiv(input) {
        // given an numeric-range input, return a div containing input and text
        // field which updates based on current value.
        var text = $("<span>").text(input.val());
        input.on("change", function() {
            text.text(input.val());
        });
        return $("<div>").append(input, text);
    }

    build_edit_settings(dom_bindings) {
        var self = this,
            editable = true;
        this.style_manager = new StyleManager(this);
        this.$div = $(dom_bindings.container);
        this.$data_div = $(dom_bindings.data_div);
        this.$settings_div = $(dom_bindings.settings_div);
        this.$display_div = $(dom_bindings.display_div);

        // rebuild visualization whenever selected
        $('a[data-toggle="tab"]').on("shown", function(e) {
            if (self.$display_div[0] === $($(e.target).attr("href"))[0]) {
                self.build_data_pivot_vis(self.$display_div, editable);
            }
        });

        this.build_data_table();
        this.build_settings();
        this.$div.fadeIn();
    }

    build_data_pivot_vis(div, editable) {
        delete this.plot;
        editable = editable || false;
        var data = JSON.parse(JSON.stringify(this.data)); // deep-copy
        this.plot = new DataPivotVisualization(data, this.settings, div, editable);
    }

    build_data_table() {
        var tbl = $('<table class="data_pivot_table">'),
            thead = $("<thead>"),
            tbody = $("<tbody>");

        // get headers
        var data_headers = [];
        for (var prop in this.data[0]) {
            // eslint-disable-next-line no-prototype-builtins
            if (this.data[0].hasOwnProperty(prop)) {
                data_headers.push(prop);
            }
        }

        // print header
        var tr = $("<tr>");
        data_headers.forEach(function(v) {
            tr.append(`<th>${v}</th>`);
        });
        thead.append(tr);

        // print body
        this.data.forEach(function(d) {
            var tr = $("<tr>");
            data_headers.forEach(function(field) {
                tr.append(`<td>${d[field]}</td>`);
            });
            tbody.append(tr);
        });

        // insert table
        tbl.append([thead, tbody]);
        this.$data_div.html(tbl);

        // now save things back to object
        this.data_headers = data_headers;
    }

    addOnRenderedCallback(cb) {
        this.onRendered.push(cb);
    }

    triggerOnRenderedCallbacks() {
        this.onRendered.forEach(cb => cb());
    }

    build_settings() {
        this.dpe_options = DataPivotExtension.get_options(this);
        var self = this,
            content = [
                $('<ul class="nav nav-tabs">').append(
                    '<li class="active"><a href="#data_pivot_settings_description" data-toggle="tab">Descriptive text columns</a></li>',
                    '<li><a href="#data_pivot_settings_data" data-toggle="tab">Visualization data</a></li>',
                    '<li><a class="dp_ordering_tab" href="#data_pivot_settings_ordering" data-toggle="tab">Data filtering and ordering</a></li>',
                    '<li><a href="#data_pivot_settings_ref" data-toggle="tab">References</a></li>',
                    '<li><a href="#data_pivot_settings_styles" data-toggle="tab">Styles</a></li>',
                    '<li><a class="dp_general_tab" href="#data_pivot_settings_general" data-toggle="tab">Other settings</a></li>'
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

        this.$settings_div.html(content).on("shown", function(e) {
            if ($(e.target).attr("href") === "#data_pivot_settings_general") {
                self._dp_settings_general.update_merge_until();
            }
            self.triggerOnRenderedCallbacks();
        });
    }

    _get_header_options(show_blank) {
        var opts = [];
        if (show_blank) opts.push(`<option value="${NULL_CASE}">${NULL_CASE}</option>`);
        return opts.concat(this.data_headers.map(v => `<option value="${v}">${v}</option>`));
    }

    _get_description_options() {
        return this.settings.description_settings.map(
            (d, i) => `<option value="${i}">${d.header_name}</option>`
        );
    }

    download_settings() {
        var settings_json = this.get_settings_json(true),
            blob = new Blob([settings_json], {
                type: "text/plain; charset=utf-8",
            });
        saveAs(blob, "data_pivot_settings.json");
    }

    get_settings_json(pretty) {
        if (pretty) {
            return JSON.stringify(this.settings, null, 4);
        } else {
            return JSON.stringify(this.settings);
        }
    }

    displayAsModal() {
        var self = this,
            modal = new HAWCModal(),
            title = `<h4>${this.title}</h4>`,
            $plot = $('<div class="span12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row-fluid">').append($plot)
            );

        modal.getModal().on("shown", function() {
            self.build_data_pivot_vis($plot);
        });

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter("")
            .show();
    }

    object_hyperlink() {
        return $("<a>")
            .attr("href", this.url)
            .attr("target", "_blank")
            .text(this.title);
    }
}

export default DataPivot;
