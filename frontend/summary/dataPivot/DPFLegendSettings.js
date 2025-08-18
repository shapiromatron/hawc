import $ from "$";
import * as d3 from "d3";
import HAWCModal from "shared/utils/HAWCModal";

import DataPivot from "./DataPivot";
import DataPivotLegend from "./DataPivotLegend";
import StyleViewer from "./StyleViewer";
import {NULL_CASE} from "./shared";

const build_tr = function (label, input) {
        return $("<tr>").append(`<th>${label}</th>`).append($("<td>").append(input));
    },
    add_horizontal_field = function (label_text, html_obj) {
        return $('<div class="form-group">')
            .append(`<label class="col-form-label">${label_text}</label>`)
            .append($('<div class="form-group">').append(html_obj));
    };

class LegendModal {
    constructor(style_manager) {
        this.style_manager = style_manager;
        this.modal = new HAWCModal();
    }
    show(style, cb) {
        const saveBtn = $(
            '<button class="btn btn-primary"aria-hidden="true">Save and Close</button>'
        ).on("click", () => {
            const $modal = this.modal.$modalDiv,
                original = $modal.data("d"),
                label = $modal.find('input[name="legend_name"]').val(),
                line_style = $modal.find('select[name="legend_line"] option:selected').val(),
                symbol_style = $modal.find('select[name="legend_symbol"] option:selected').val(),
                rect_style = $modal.find('select[name="legend_rect"] option:selected').val(),
                modified = {line_style, symbol_style, rect_style, label};

            if (label === "") {
                alert("Error - name must not be blank");
                return;
            }

            if (
                line_style === NULL_CASE &&
                symbol_style === NULL_CASE &&
                rect_style === NULL_CASE
            ) {
                alert("Error - at least one style must be selected");
                return;
            }

            cb(original, modified);
            this.modal.hide();
        });

        this.modal
            .addHeader("<h3>Modify legend entry</h3>")
            .addBody(
                `<div class="container-fluid">
                    <div class="style_plot" style="margin-left:180px; height: 70px;"></div>
                    <br>
                    <div class="legend_fields"></div>
                </div>`
            )
            .addFooter(saveBtn)
            .show({}, () => this.draw_modal_fields(style));
    }
    draw_modal_fields(d) {
        const $modal = this.modal.$modalDiv,
            tmp_label = d ? d.label : NULL_CASE,
            tmp_line = d ? d.line_style : NULL_CASE,
            tmp_symbol = d ? d.symbol_style : NULL_CASE,
            tmp_rect = d ? d.rect_style : NULL_CASE,
            name = $(`<input name="legend_name" class="form-control" value="${tmp_label}">`),
            line = this.style_manager
                .add_select("lines", tmp_line, true)
                .attr("name", "legend_line"),
            symbol = this.style_manager
                .add_select("symbols", tmp_symbol, true)
                .attr("name", "legend_symbol"),
            rectangle = this.style_manager
                .add_select("rectangles", tmp_rect, true)
                .attr("name", "legend_rect"),
            svgDiv = $modal.find(".style_plot"),
            get_style_object = () => {
                return {
                    type: "legend",
                    line_style: line.find("option:selected").data("d"),
                    symbol_style: symbol.find("option:selected").data("d"),
                    rect_style: rectangle.find("option:selected").data("d"),
                };
            },
            viewer = new StyleViewer(svgDiv, get_style_object()),
            update_viewer = () => viewer.apply_new_styles(get_style_object(), false);

        $modal.removeData("d");
        if (d) {
            $modal.data("d", d);
        }

        $modal
            .find(".legend_fields")
            .html([
                add_horizontal_field("Legend name", name),
                add_horizontal_field("Symbol style", symbol),
                add_horizontal_field("Line style", line),
                add_horizontal_field("Rectangle style", rectangle),
            ]);

        line.on("change", update_viewer);
        symbol.on("change", update_viewer);
        rectangle.on("change", update_viewer);
    }
}

class LegendSettings {
    constructor(dp) {
        this.dp = dp;
        this.container = null;
        this.plot_div = $('<div class="col-md-6">');
        const svg = d3
                .select(this.plot_div[0])
                .append("svg")
                .attr("role", "image")
                .attr("aria-label", "A chart legend")
                .attr("width", "95%")
                .attr("height", "300px")
                .attr("class", "d3"),
            vis = svg.append("g").attr("transform", "translate(10,10)");
        this.legend = new DataPivotLegend(
            svg.node(),
            vis,
            this.dp.settings.legend,
            this.dp.settings
        );
        this.modal = new LegendModal(this.dp.style_manager);
    }
    render() {
        const dp = this.dp,
            settings = dp.settings.legend,
            legend = this.legend,
            div = $('<div class="row">'),
            content = $('<div class="col-md-6">'),
            tbl = $('<table class="table table-sm table-bordered">'),
            tbody = $("<tbody>"),
            colgroup = $('<colgroup><col style="width: 30%;"><col style="width: 70%;">'),
            show_legend = $('<input type="checkbox">')
                .prop("checked", settings.show)
                .on("change", function () {
                    settings.show = $(this).prop("checked");
                }),
            number_columns = $(
                `<input class="form-control" type="range" min="1" max="5" value="${settings.columns}">`
            ).on("change", function () {
                settings.columns = parseInt($(this).val()) || 1;
                legend._draw_legend();
            }),
            left = $("<input type='number' class='form-control'>")
                .val(settings.left)
                .on("change", function () {
                    settings.left = parseInt($(this).val()) || 1;
                    legend._draw_legend();
                }),
            top = $("<input type='number' class='form-control'>")
                .val(settings.top)
                .on("change", function () {
                    settings.top = parseInt($(this).val(), 10) || 1;
                    legend._draw_legend();
                }),
            border_width = $(
                `<input class="form-control" type="range" min="0" max="10" value="${settings.style.border_width}">`
            ).on("change", function () {
                settings.style.border_width = parseFloat($(this).val(), 10) || 0;
                legend._draw_legend();
            }),
            border_color = $(
                `<input class="form-control" name="fill" type="color" value="${settings.style.border_color}">`
            ).on("change", function () {
                settings.style.border_color = $(this).val();
                legend._draw_legend();
            }),
            button_well = $('<div class="well">'),
            legend_item = legend.add_select(),
            legend_item_up = $(
                '<button class="btn btn-light"><i class="fa fa-arrow-up"></i></button>'
            ).on("click", function () {
                legend.move_field(legend_item.find("option:selected").data("d"), -1);
                legend._draw_legend();
            }),
            legend_item_down = $(
                '<button class="btn btn-light"><i class="fa fa-arrow-down"></i></button>'
            ).on("click", function () {
                legend.move_field(legend_item.find("option:selected").data("d"), 1);
                legend._draw_legend();
            }),
            legend_item_delete = $('<button class="btn btn-danger">Delete</button>').on(
                "click",
                function () {
                    legend.delete_field(legend_item.find("option:selected").data("d"));
                    legend._draw_legend();
                }
            ),
            handleSave = (original, modified) => {
                this.legend.add_or_update_field(modified, original);
                this.legend._draw_legend();
            },
            legend_item_new = $('<button class="btn btn-primary">New</button>').on("click", () => {
                const style = undefined;
                this.modal.show(style, handleSave);
            }),
            legend_item_edit = $('<button class="btn btn-info">Edit</button>').on("click", () => {
                const style = legend_item.find("option:selected").data("d");
                this.modal.show(style, handleSave);
            });

        tbody.html([
            build_tr("Show legend", show_legend),
            build_tr("Number of columns", DataPivot.rangeInputDiv(number_columns)),
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
        div.html([content, this.plot_div]);

        this.container = div;

        return div;
    }
    update_legend() {
        this.legend._draw_legend();
    }
}

export default LegendSettings;
