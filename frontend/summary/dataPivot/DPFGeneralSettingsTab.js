import $ from "$";
import * as d3 from "d3";
import DataPivotLegend from "./DataPivotLegend";
import {_DataPivot_settings_general} from "./DataPivotUtilities";
import {NULL_CASE} from "./shared";
import StyleViewer from "./StyleViewer";
import DataPivot from "./DataPivot";

let build_settings_general_tab = function(self) {
    var tab = $('<div class="tab-pane" id="data_pivot_settings_general">'),
        build_general_settings = function() {
            var div = $("<div>"),
                tbl = $('<table class="table table-condensed table-bordered">'),
                tbody = $("<tbody>"),
                colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;">');

            self._dp_settings_general = new _DataPivot_settings_general(
                self,
                self.settings.plot_settings
            );
            tbody.html(self._dp_settings_general.trs);
            tbl.html([colgroup, tbody]);
            return div.html(tbl);
        },
        build_download_button = function() {
            return $('<button class="btn btn-primary">Download settings</button>').on(
                "click",
                function() {
                    self.download_settings();
                }
            );
        },
        build_legend_settings = function() {
            var div = $('<div class="row-fluid">'),
                content = $('<div class="span6">'),
                plot_div = $('<div class="span6">'),
                vis = d3
                    .select(plot_div[0])
                    .append("svg")
                    .attr("width", "95%")
                    .attr("height", "300px")
                    .attr("class", "d3")
                    .append("g")
                    .attr("transform", "translate(10,10)");

            self.legend = new DataPivotLegend(vis, self.settings.legend, self.settings);

            var tbl = $('<table class="table table-condensed table-bordered">'),
                tbody = $("<tbody>"),
                colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;">'),
                build_tr = function(label, input) {
                    return $("<tr>")
                        .append(`<th>${label}</th>`)
                        .append($("<td>").append(input));
                },
                add_horizontal_field = function(label_text, html_obj) {
                    return $('<div class="control-group">')
                        .append(`<label class="control-label">${label_text}</label>`)
                        .append($('<div class="controls">').append(html_obj));
                },
                show_legend = $('<input type="checkbox">')
                    .prop("checked", self.settings.legend.show)
                    .on("change", function() {
                        self.settings.legend.show = $(this).prop("checked");
                    }),
                number_columns = $("<input>")
                    .val(self.settings.legend.columns)
                    .on("change", function() {
                        self.settings.legend.columns = parseInt($(this).val(), 10) || 1;
                        self.legend._draw_legend();
                    }),
                left = $("<input>")
                    .val(self.settings.legend.left)
                    .on("change", function() {
                        self.settings.legend.left = parseInt($(this).val(), 10) || 1;
                        self.legend._draw_legend();
                    }),
                top = $("<input>")
                    .val(self.settings.legend.top)
                    .on("change", function() {
                        self.settings.legend.top = parseInt($(this).val(), 10) || 1;
                        self.legend._draw_legend();
                    }),
                border_width = $(
                    `<input type="range" min="0" max="10" value="${self.settings.legend.style.border_width}">`
                ).on("change", function() {
                    self.settings.legend.style.border_width = parseFloat($(this).val(), 10) || 0;
                    self.legend._draw_legend();
                }),
                border_color = $(
                    `<input name="fill" type="color" value="${self.settings.legend.style.border_color}">`
                ).on("change", function() {
                    self.settings.legend.style.border_color = $(this).val();
                    self.legend._draw_legend();
                }),
                modal = $(`<div class="modal hide fade">
                              <div class="modal-header">
                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                                <h3>Modify Legend Entry</h3>
                              </div>
                            <div class="modal-body">
                              <form class="form-horizontal">
                                <div class="style_plot" style="margin-left:180px; height: 70px;"></div>
                                <br>
                                <div class="legend_fields"></div>
                              </form>
                              <div class="modal-footer">
                                <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
                              </div>
                            </div>`),
                button_well = $('<div class="well">'),
                draw_modal_fields = function(d) {
                    if (d) {
                        modal.data("d", d);
                    } else {
                        modal.removeData("d");
                    }
                    var tmp_label = d ? d.label : NULL_CASE,
                        tmp_line = d ? d.line_style : NULL_CASE,
                        tmp_symbol = d ? d.symbol_style : NULL_CASE,
                        tmp_rect = d ? d.rect_style : NULL_CASE,
                        name = $(`<input name="legend_name" value="${tmp_label}">`),
                        line = self.style_manager
                            .add_select("lines", tmp_line, true)
                            .removeClass("span12")
                            .attr("name", "legend_line"),
                        symbol = self.style_manager
                            .add_select("symbols", tmp_symbol, true)
                            .removeClass("span12")
                            .attr("name", "legend_symbol"),
                        rectangle = self.style_manager
                            .add_select("rectangles", tmp_rect, true)
                            .removeClass("span12")
                            .attr("name", "legend_rect");

                    modal
                        .find(".legend_fields")
                        .html([
                            add_horizontal_field("Legend name", name),
                            add_horizontal_field("Symbol style", symbol),
                            add_horizontal_field("Line style", line),
                            add_horizontal_field("Rectangle style", rectangle),
                        ]);

                    var svgdiv = modal.find(".style_plot"),
                        build_style_obj = function() {
                            return {
                                type: "legend",
                                line_style: line.find("option:selected").data("d"),
                                symbol_style: symbol.find("option:selected").data("d"),
                                rect_style: rectangle.find("option:selected").data("d"),
                            };
                        },
                        viewer = new StyleViewer(svgdiv, build_style_obj()),
                        update_viewer = function() {
                            viewer.apply_new_styles(build_style_obj(), false);
                        };

                    line.on("change", update_viewer);
                    symbol.on("change", update_viewer);
                    rectangle.on("change", update_viewer);
                },
                legend_item = self.legend.add_select(),
                legend_item_up = $('<button><i class="icon-arrow-up"></i></button>').on(
                    "click",
                    function() {
                        self.legend.move_field(legend_item.find("option:selected").data("d"), -1);
                        self.legend._draw_legend();
                    }
                ),
                legend_item_down = $('<button><i class="icon-arrow-down"></i></button>').on(
                    "click",
                    function() {
                        self.legend.move_field(legend_item.find("option:selected").data("d"), 1);
                        self.legend._draw_legend();
                    }
                ),
                legend_item_new = $('<button class="btn btn-primary">New</button>').on(
                    "click",
                    function() {
                        modal.modal("show");
                        draw_modal_fields(undefined);
                        self.legend._draw_legend();
                    }
                ),
                legend_item_edit = $('<button class="btn btn-info">Edit</button>').on(
                    "click",
                    function() {
                        modal.modal("show");
                        draw_modal_fields(legend_item.find("option:selected").data("d"));
                        self.legend._draw_legend();
                    }
                ),
                legend_item_delete = $('<button class="btn btn-danger">Delete</button>').on(
                    "click",
                    function() {
                        self.legend.delete_field(legend_item.find("option:selected").data("d"));
                        self.legend._draw_legend();
                    }
                ),
                save_legend_item = $(
                    '<button class="btn btn-primary"aria-hidden="true">Save and Close</button>'
                ).on("click", function() {
                    var label = modal.find('input[name="legend_name"]').val(),
                        line_style = modal.find('select[name="legend_line"] option:selected').val(),
                        symbol_style = modal
                            .find('select[name="legend_symbol"] option:selected')
                            .val(),
                        rect_style = modal.find('select[name="legend_rect"] option:selected').val();

                    if (
                        label === "" ||
                        (line_style === NULL_CASE &&
                            symbol_style === NULL_CASE &&
                            rect_style === NULL_CASE)
                    ) {
                        alert(
                            "Error - name must not be blank, and at least one style must be selected"
                        );
                        return;
                    }

                    var d = modal.data("d"),
                        obj = {line_style, symbol_style, rect_style, label};

                    self.legend.add_or_update_field(obj, d);
                    modal.modal("hide");
                    self.legend._draw_legend();
                });

            modal.find(".modal-footer").append(save_legend_item);
            tbody.html([
                build_tr("Show legend", show_legend),
                build_tr("Number of columns", number_columns),
                build_tr("Border width", DataPivot.rangeInputDiv(border_width)),
                build_tr("Border color", border_color),
                build_tr("X-location on figure", left),
                build_tr("Y-location on figure", top),
                build_tr("Legend item", legend_item),
            ]);

            tbl.html([colgroup, tbody]);
            button_well.append(
                legend_item_new,
                legend_item_up,
                legend_item_down,
                legend_item_edit,
                legend_item_delete
            );
            content.append("<h4>Legend Settings<h4>", tbl, button_well);
            div.html([content, plot_div]);
            div.find('input[type="color"]').spectrum({showInitial: true, showInput: true});
            return div;
        };

    // update whenever tab is clicked
    var legend_div = build_legend_settings();
    self.$div.on("shown", 'a.dp_general_tab[data-toggle="tab"]', function() {
        self.legend._draw_legend();
    });

    return tab.html([
        build_general_settings(),
        "<hr>",
        legend_div,
        "<hr>",
        build_download_button(),
    ]);
};

export default build_settings_general_tab;
