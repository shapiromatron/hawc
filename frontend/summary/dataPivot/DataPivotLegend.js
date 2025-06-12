import * as d3 from "d3";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

import {applyStyles} from "../summary/common";
import {StyleLine, StyleRectangle, StyleSymbol} from "./Styles";
import {NULL_CASE} from "./shared";

class DataPivotLegend {
    constructor(svg, vis, settings, dp_settings, options) {
        this.svg = svg;
        this.vis = vis;
        this.settings = settings;
        this.dp_settings = dp_settings;
        this.selects = [];
        this.options = options || {offset: false};
        if (this.settings.show) {
            this._draw_legend();
        }
    }

    static default_settings() {
        return {
            show: true,
            left: 5,
            top: 5,
            columns: 1,
            style: {border_color: "#666666", border_width: "2px"},
            fields: [],
        };
    }

    add_select() {
        var select = $("<select class='form-control'>").html(this._build_options());
        this.selects.push(select);
        return select;
    }

    _update_selects() {
        for (var i = 0; i < this.selects.length; i++) {
            var select = this.selects[i],
                sel = select.find("option:selected").val();
            select.html(this._build_options());
            select.find(`option[value="${sel}"]`).prop("selected", true);
        }
    }

    _build_options() {
        return this.settings.fields.map(function (v) {
            return $(`<option value="${v.label}">${v.label}</option>`).data("d", v);
        });
    }

    _draw_legend() {
        if (this.legend) {
            this.legend.remove();
            delete this.legend;
        }

        var self = this,
            cursor = this.options.editable ? "pointer" : "auto",
            buffer = 5,
            apply_styles = function (d) {
                applyStyles(self.svg, this, d.style);
            },
            drag = !this.options.editable
                ? function () {}
                : HAWCUtils.updateDragLocationTransform(function (x, y) {
                      self.settings.left = parseInt(x, 10);
                      self.settings.top = parseInt(y, 10);
                  });

        this.legend = this.vis.append("g");

        if (this.options.offset) {
            this.legend
                .attr("cursor", cursor)
                .attr("transform", `translate(${self.settings.left},${self.settings.top})`)
                .call(drag);
        }

        this.legend
            .append("svg:rect")
            .attr("stroke-width", this.settings.style.border_width)
            .attr("stroke", this.settings.style.border_color)
            .attr("fill", "white")
            .attr("height", 10)
            .attr("width", 10);

        var vertical_spacing = 22,
            text_x_offset,
            columns = this.settings.columns,
            rows = Math.ceil(this.settings.fields.length / columns),
            style,
            colg,
            row_index;

        this.legend_columns = [];

        // add bars
        this.settings.fields.forEach(function (datum, i) {
            if (i % rows === 0) {
                colg = self.legend.append("g");
                self.legend_columns.push(colg);
                row_index = 0;
            }

            // add rectangle
            if (datum.rect_style !== NULL_CASE) {
                text_x_offset = 15;
                style = self._get_rect_style(datum);
                colg.selectAll()
                    .data([
                        {
                            x: buffer * 0.5,
                            y: (row_index + 0.25) * vertical_spacing,
                            width: text_x_offset + buffer,
                            height: vertical_spacing * 0.5,
                            style,
                        },
                    ])
                    .enter()
                    .append("svg:rect")
                    .attr("x", d => d.x)
                    .attr("y", d => d.y)
                    .attr("width", d => d.width)
                    .attr("height", d => d.height)
                    .each(apply_styles);
            }

            // add line
            if (datum.line_style !== NULL_CASE) {
                text_x_offset = 15;
                style = self._get_line_style(datum);
                colg.selectAll()
                    .data([
                        {
                            x1: buffer,
                            x2: buffer + text_x_offset,
                            y1: (row_index + 0.5) * vertical_spacing,
                            y2: (row_index + 0.5) * vertical_spacing,
                            style,
                        },
                        {
                            x1: buffer,
                            x2: buffer,
                            y1: (row_index + 0.25) * vertical_spacing,
                            y2: (row_index + 0.75) * vertical_spacing,
                            style,
                        },
                        {
                            x1: buffer + text_x_offset,
                            x2: buffer + text_x_offset,
                            y1: (row_index + 0.25) * vertical_spacing,
                            y2: (row_index + 0.75) * vertical_spacing,
                            style,
                        },
                    ])
                    .enter()
                    .append("svg:line")
                    .attr("x1", v => v.x1)
                    .attr("x2", v => v.x2)
                    .attr("y1", v => v.y1)
                    .attr("y2", v => v.y2)
                    .each(apply_styles);
            }

            // add symbol
            if (datum.symbol_style !== NULL_CASE) {
                text_x_offset = 15;
                style = self._get_symbol_style(datum);
                colg.selectAll()
                    .data([
                        {
                            x: buffer + text_x_offset / 2,
                            y: (row_index + 0.5) * vertical_spacing,
                            style,
                        },
                    ])
                    .enter()
                    .append("path")
                    .attr(
                        "d",
                        d3.symbol().size(style.size).type(HAWCUtils.symbolStringToType(style.type))
                    )
                    .attr("transform", d => `translate(${d.x},${d.y})`)
                    .each(apply_styles);
            }

            // add text
            text_x_offset = 15;
            colg.selectAll()
                .data([self.settings.fields[i]])
                .enter()
                .append("svg:text")
                .attr("x", 2 * buffer + text_x_offset)
                .attr("class", "legend_text")
                .attr("dy", "3.5px")
                .attr("y", (row_index + 0.5) * vertical_spacing)
                .text(d => d.label);

            row_index += 1;
        });

        var offset = 0;
        for (var i = 1; i < this.legend_columns.length; i++) {
            offset += this.legend_columns[i - 1].node().getBoundingClientRect().width + buffer;
            this.legend_columns[i].attr("transform", `translate(${offset},0)`);
        }

        var resize_legend = function () {
            var dim = self.legend.node().getBoundingClientRect();
            self.legend
                .select("rect")
                .attr("width", dim.width + buffer)
                .attr("height", dim.height + buffer);
        };

        resize_legend();
    }

    add_or_update_field(obj, legend_item) {
        if (isFinite(obj.symbol_index)) {
            legend_item = this.settings.fields.filter(function (v) {
                return v.symbol_index === obj.symbol_index;
            })[0];
        }

        if (isFinite(obj.line_index)) {
            legend_item = this.settings.fields.filter(v => v.line_index === obj.line_index)[0];
        }

        if (obj.keyField !== undefined) {
            legend_item = this.settings.fields.filter(v => v.keyField === obj.keyField)[0];
        }

        if (legend_item) {
            for (var key in obj) {
                legend_item[key] = obj[key];
            }
        } else {
            if (!obj.line_style) obj.line_style = NULL_CASE;
            if (!obj.symbol_style) obj.symbol_style = NULL_CASE;
            if (!obj.rect_style) obj.rect_style = NULL_CASE;
            this.settings.fields.push(obj);
        }
        this._update_selects();
    }

    _get_symbol_style(field) {
        return (
            this.dp_settings.styles.symbols.filter(v => v.name === field.symbol_style)[0] ||
            StyleSymbol.default_settings()
        );
    }

    _get_line_style(field) {
        return (
            this.dp_settings.styles.lines.filter(v => v.name === field.line_style)[0] ||
            StyleLine.default_settings()
        );
    }

    _get_rect_style(field) {
        return (
            this.dp_settings.styles.rectangles.filter(v => v.name === field.rect_style)[0] ||
            StyleRectangle.default_settings()
        );
    }

    move_field(obj, offset) {
        var fields = this.settings.fields;
        for (var i = 0; i < fields.length; i++) {
            if (fields[i] === obj) {
                var new_off = i + offset;
                if (new_off >= fields.length) new_off = fields.length - 1;
                if (new_off < 0) new_off = 0;
                fields.splice(new_off, 0, fields.splice(i, 1)[0]);
                return;
            }
        }
        this._update_selects();
    }

    delete_field(obj) {
        for (var i = 0; i < this.settings.fields.length; i++) {
            if (this.settings.fields[i] === obj) {
                this.settings.fields.splice(i, 1);
                break;
            }
        }
        this._update_selects();
    }
}

export default DataPivotLegend;
