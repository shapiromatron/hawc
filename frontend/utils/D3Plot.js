import $ from "$";
import * as d3 from "d3";

import h from "shared/utils/helpers";

// Generic parent for all d3.js visualizations
class D3Plot {
    add_title(x, y) {
        x = x || this.w / 2;
        y = y || -this.padding.top / 2;

        if (this.title) {
            this.title.remove();
        }
        this.title = this.vis
            .append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("text-anchor", "middle")
            .attr("class", "dr_title")
            .html(this.title_str);
    }

    add_final_rectangle() {
        // Add final rectangle around plot.
        if (this.bounding_rectangle) this.bounding_rectangle.remove();
        this.bounding_rectangle = this.vis
            .append("rect")
            .attr("width", this.w)
            .attr("height", this.h)
            .attr("class", "bounding_rectangle");
    }

    set_legend_location(top, left) {
        this.legend_top = top;
        this.legend_left = left;
    }

    build_legend(settings) {
        var plot = this,
            buffer = settings.box_padding, //shortcut reference
            drag = d3.drag().on("drag", function(d, i) {
                var regexp = /\((-?[0-9]+)[, ](-?[0-9]+)\)/,
                    p = d3.select(this),
                    m = regexp.exec(p.attr("transform"));

                if (m !== null && m.length === 3) {
                    var x = parseFloat(m[1]) + d3.event.dx,
                        y = parseFloat(m[2]) + d3.event.dy;
                    p.attr("transform", `translate(${x},${y})`);
                    plot.set_legend_location(y, x);
                }
            });

        if (this.legend) {
            this.legend.node().remove();
        }

        this.legend = this.vis
            .append("g")
            .attr("class", "plot_legend")
            .attr("transform", `translate(${settings.box_l},${settings.box_t})`)
            .attr("cursor", "pointer")
            .attr("data-buffer", buffer)
            .call(drag);

        this.set_legend_location(settings.box_t, settings.box_l);

        this.legend
            .append("svg:rect")
            .attr("class", "legend")
            .attr("height", 10)
            .attr("width", 10);

        this.legend
            .selectAll("legend_circles")
            .data(settings.items)
            .enter()
            .append("circle")
            .attr("cx", settings.dot_r + buffer)
            .attr("cy", (d, i) => buffer * 2 + i * settings.item_height)
            .attr("r", settings.dot_r)
            .attr("class", d => "legend_circle " + d.classes)
            .attr("fill", d => d.color);

        this.legend
            .selectAll("legend_text")
            .data(settings.items)
            .enter()
            .append("svg:text")
            .attr("x", 2 * settings.dot_r + buffer * 2)
            .attr("class", "legend_text")
            .attr("y", (d, i) => buffer * 2 + settings.dot_r + i * settings.item_height)
            .text(d => d.text);

        this.resize_legend();
    }

    resize_legend() {
        // resize legend box that encompasses legend items
        // NOTE that this requires the image to be rendered into DOM
        if (this.legend) {
            var buffer = parseInt(this.legend.attr("data-buffer")),
                dim = this.legend.node().getBoundingClientRect();

            this.legend
                .select(".legend")
                .attr("width", dim.width + buffer)
                .attr("height", dim.height + buffer);
        }
    }

    build_plot_skeleton(background) {
        //Basic plot setup to set size and positions
        var self = this,
            w = this.w + this.padding.left + this.padding.right,
            h = this.h + this.padding.top + this.padding.bottom;

        //clear plot div and and append new svg object
        this.plot_div.empty();

        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("width", w)
            .attr("height", h)
            .attr("class", "d3")
            .attr("viewBox", `0 0 ${w} ${h}`)
            .attr("preserveAspectRatio", "xMinYMin")
            .node();

        this.vis = d3
            .select(this.svg)
            .append("g")
            .attr("transform", `translate(${this.padding.left},${this.padding.top})`);

        var chart = $(this.svg),
            container = chart.parent();

        this.full_width = w;
        this.full_height = h;
        this.isFullSize = true;
        this.trigger_resize = function(forceResize) {
            var targetWidth = Math.min(container.width(), self.full_width),
                aspect = self.full_width / self.full_height;
            if (forceResize === true && !self.isFullSize) targetWidth = self.full_width;

            if (targetWidth !== self.full_width) {
                // use custom smaller size
                chart.attr("width", targetWidth);
                chart.attr("height", Math.round(targetWidth / aspect));
                self.isFullSize = false;
                if (self.resize_button) {
                    self.resize_button.attr("title", "zoom figure to full-size");
                    self.resize_button.find("i").attr("class", "icon-zoom-in");
                }
            } else {
                // set back to full-size
                chart.attr("width", self.full_width);
                chart.attr("height", self.full_height);
                self.isFullSize = true;
                if (self.resize_button) {
                    self.resize_button.attr("title", "zoom figure to fit screen");
                    self.resize_button.find("i").attr("class", "icon-zoom-out");
                }
            }
        };
        $(window).resize(this.trigger_resize);

        // add gray background to plot.
        if (background) {
            this.vis
                .append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("height", this.h)
                .attr("width", this.w)
                .attr("class", "dp_bg");
        }
    }

    build_x_label(x, y) {
        x = x || this.w / 2;
        y = y || this.h + this.padding.bottom - 5;

        if (this.x_axis_label) {
            this.x_axis_label.remove();
        }
        this.x_axis_label = this.vis
            .append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("text-anchor", "middle")
            .attr("class", "dr_axis_labels x_axis_label")
            .text(this.x_label_text);
    }

    build_y_label(x, y) {
        x = x || -this.h / 2;
        y = y || -this.padding.left + 15;

        if (this.y_axis_label) {
            this.y_axis_label.remove();
        }
        this.y_axis_label = this.vis
            .append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("transform", "rotate(270)")
            .attr("text-anchor", "middle")
            .attr("class", "dr_axis_labels y_axis_label")
            .text(this.y_label_text);
    }

    _build_scale(settings) {
        var scale;
        switch (settings.scale_type) {
            case "log":
                scale = d3
                    .scaleLog()
                    .clamp(true)
                    .domain(settings.domain)
                    .rangeRound(settings.rangeRound)
                    .nice();
                break;
            case "linear":
                scale = d3
                    .scaleLinear()
                    .clamp(true)
                    .domain(settings.domain)
                    .rangeRound(settings.rangeRound)
                    .nice();
                break;
            case "ordinal":
                scale = d3
                    .scaleBand()
                    .domain(settings.domain)
                    .rangeRound(settings.rangeRound);
                break;
            default:
                throw `scale type not defined: ${settings.scale_type}`;
        }
        return scale;
    }

    _print_axis(axisFunc, scale, settings) {
        const axis = axisFunc(scale);

        switch (settings.scale_type) {
            case "log":
                axis.ticks(h.numLogTicks(settings.domain), settings.label_format);
                break;
            case "linear":
                axis.ticks(settings.number_ticks);
                if (settings.label_format !== undefined) {
                    axis.tickFormat(settings.label_format);
                }
                break;
        }

        if (settings.axis_labels) {
            this.vis
                .append("g")
                .attr("transform", `translate(${settings.x_translate},${settings.y_translate})`)
                .attr("class", settings.axis_class)
                .call(axis);
        }
        return axis;
    }

    _print_gridlines(scale, settings, line_settings) {
        if (!settings.gridlines) {
            return undefined;
        }

        var gridline_data;
        switch (settings.scale_type) {
            case "log":
            case "linear":
                gridline_data = scale.ticks(settings.number_ticks);
                break;
            case "ordinal":
                gridline_data = scale.domain();
                break;
        }

        var gridlines = this.vis.append("g").attr("class", settings.gridline_class);

        gridlines
            .selectAll("gridlines")
            .data(gridline_data)
            .enter()
            .append("svg:line")
            .attr("x1", line_settings[0])
            .attr("x2", line_settings[1])
            .attr("y1", line_settings[2])
            .attr("y2", line_settings[3])
            .attr("class", settings.gridline_class);

        return gridlines;
    }

    rebuild_y_gridlines(options) {
        // rebuild y-gridlines

        var duration = options.animate ? 1000 : 0;

        this.y_primary_gridlines = this.vis
            .select("g.y_gridlines")
            .selectAll("line")
            .data(this.y_scale.ticks(this.y_axis_settings.number_ticks));

        this.y_primary_gridlines
            .enter()
            .append("line")
            .attr("class", this.y_axis_settings.gridline_class)
            .attr("y1", function(v) {
                return v;
            })
            .attr("y2", function(v) {
                return v;
            })
            .attr("x1", 0)
            .attr("x2", 0);

        this.y_primary_gridlines
            .transition()
            .duration(duration)
            .attr("y1", this.y_scale)
            .attr("y2", this.y_scale)
            .attr("x2", this.w);

        this.y_primary_gridlines
            .exit()
            .transition()
            .duration(duration / 2)
            .attr("x2", 0)
            .remove();
    }

    rebuild_x_gridlines(options) {
        // rebuild x-gridlines

        var duration = options.animate ? 1000 : 0;

        this.x_primary_gridlines = this.vis
            .select("g.x_gridlines")
            .selectAll("line")
            .data(this.x_scale.ticks(this.x_axis_settings.number_ticks));

        this.x_primary_gridlines
            .enter()
            .append("line")
            .attr("class", this.x_axis_settings.gridline_class)
            .attr("x1", v => v)
            .attr("x2", v => v)
            .attr("y1", 0)
            .attr("y2", 0);

        this.x_primary_gridlines
            .transition()
            .duration(duration)
            .attr("x1", this.x_scale)
            .attr("x2", this.x_scale)
            .attr("y2", this.h);

        this.x_primary_gridlines
            .exit()
            .transition()
            .duration(duration / 2)
            .attr("y2", 0)
            .remove();
    }

    build_y_axis() {
        // build y-axis based on plot-settings
        this.y_scale = this._build_scale(this.y_axis_settings);
        this.yAxis = this._print_axis(
            this.getAxisType(this.y_axis_settings.text_orient),
            this.y_scale,
            this.y_axis_settings
        );
        this.y_primary_gridlines = this._print_gridlines(this.y_scale, this.y_axis_settings, [
            0,
            this.w,
            this.y_scale,
            this.y_scale,
        ]);
    }

    getAxisType(val) {
        switch (val) {
            case "top":
                return d3.axisTop;
            case "bottom":
                return d3.axisBottom;
            case "left":
                return d3.axisLeft;
            default:
                throw `Unknown axis type ${val}`;
        }
    }

    build_x_axis(axisType) {
        // build x-axis based on plot-settings
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.xAxis = this._print_axis(
            this.getAxisType(this.x_axis_settings.text_orient),
            this.x_scale,
            this.x_axis_settings
        );
        this.x_primary_gridlines = this._print_gridlines(this.x_scale, this.x_axis_settings, [
            this.x_scale,
            this.x_scale,
            0,
            this.h,
        ]);
    }

    build_line(options, existing) {
        // build or update an existing line
        var l = existing;
        if (existing) {
            existing
                .data(options.data || l.data())
                .transition()
                .delay(options.delay || 0)
                .duration(options.duration || 1000)
                .attr(
                    "x1",
                    options.x1 ||
                        function(v, i) {
                            return d3.select(this).attr("x1");
                        }
                )
                .attr(
                    "x2",
                    options.x2 ||
                        function(v, i) {
                            return d3.select(this).attr("x2");
                        }
                )
                .attr(
                    "y1",
                    options.y1 ||
                        function(v, i) {
                            return d3.select(this).attr("y1");
                        }
                )
                .attr(
                    "y2",
                    options.y2 ||
                        function(v, i) {
                            return d3.select(this).attr("y2");
                        }
                );
        } else {
            var append_to = options.append_to || this.vis;
            l = append_to
                .selectAll("svg.bars")
                .data(options.data)
                .enter()
                .append("line")
                .attr("x1", options.x1)
                .attr("y1", options.y1)
                .attr("x2", options.x2)
                .attr("y2", options.y2)
                .attr("class", options.classes);
        }
        return l;
    }

    isWithinDomain(event) {
        // check that event is within plot domain
        var v = d3.mouse(event);
        return !(v[1] > this.h || v[1] < 0 || v[0] < 0 || v[0] > this.w);
    }

    add_menu() {
        if (this.menu_div) return; // singleton
        var plot = this;

        // show cog to toggle options menu
        this.cog = this.vis
            .append("foreignObject")
            .attr("x", this.w + this.padding.right - 20)
            .attr("y", -this.padding.top + 5)
            .attr("width", 30)
            .attr("height", 30);

        this.cog_button = this.cog
            .append("xhtml:a")
            .attr("title", "Display plot menu")
            .attr("class", "hidden")
            .on("click", function(v, i) {
                plot._toggle_menu_bar();
            });
        this.cog_button.append("xhtml:i").attr("class", "icon-cog");

        // add menu below div
        this.menu_div = $('<div class="options_menu"></div>');
        this.plot_div.append(this.menu_div);

        // add close button to menu
        var close_button = {
            id: "close",
            cls: "btn btn-mini pull-right",
            title: "Hide menu",
            text: "x",
            on_click() {
                plot._toggle_menu_bar();
            },
        };
        this.add_menu_button(close_button);

        this._add_download_buttons();

        // add zoom button to menu
        var zoom_button = {
            id: "close",
            cls: "btn btn-mini pull-right",
            title: "Zoom image to full-size",
            text: "",
            icon: "icon-zoom-in",
            on_click() {
                plot.trigger_resize(true);
            },
        };
        this.resize_button = this.add_menu_button(zoom_button);
    }

    _add_download_buttons() {
        var plot = this,
            group = $('<div class="pull-right btn-group"></div>'),
            dropdown = $(
                '<a title="Download figure" class="btn btn-mini dropdown-toggle" data-toggle="dropdown" href="#"><i class="icon-download-alt"></i></a>'
            ),
            dropdown_li = $('<ul class="dropdown-menu"></ul>'),
            svg = $("<li>")
                .append('<a href="#">Download as a SVG</a>')
                .on("click", function(e) {
                    e.preventDefault();
                    plot._download_image({format: "svg"});
                }),
            pptx = $("<li>")
                .append('<a href="#">Download as a PPTX</a>')
                .on("click", function(e) {
                    e.preventDefault();
                    plot._download_image({format: "pptx"});
                }),
            png = $("<li>")
                .append('<a href="#">Download as a PNG</a>')
                .on("click", function(e) {
                    e.preventDefault();
                    plot._download_image({format: "png"});
                }),
            pdf = $("<li>")
                .append('<a href="#">Download as a PDF</a>')
                .on("click", function(e) {
                    e.preventDefault();
                    plot._download_image({format: "pdf"});
                });
        dropdown_li.append(svg, pptx, png, pdf);
        group.append(dropdown, dropdown_li);
        this.menu_div.append(group);
    }

    add_menu_button(options) {
        // add a button to the options menu
        var a = $("<a></a>")
            .attr("id", options.id)
            .attr("class", options.cls)
            .attr("title", options.title)
            .text(options.text || "")
            .on("click", options.on_click);
        if (options.icon) {
            var icon = $("<i></i>").addClass(options.icon);
            a.append(icon);
        }
        this.menu_div.append(a);
        return a;
    }

    _toggle_menu_bar() {
        $(this.menu_div).toggleClass("hidden");
        $(this.cog_button).toggleClass("hidden");
    }

    _download_image(options) {
        var svg_blob = this._save_to_svg(),
            form = $(
                '<form style="display: none;" action="/assessment/download-plot/" method="post"></form>'
            ).html([
                `<input name="height" value="${svg_blob.height}">`,
                `<input name="width" value="${svg_blob.width}">`,
                `<input name="svg" value="${btoa(escape(svg_blob.source[0]))}">`,
                `<input name="output" value="${options.format}">`,
            ]);
        form.appendTo("body").submit();
    }

    _save_to_svg() {
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: http://nytimes.github.com/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.

        function get_selected_svg(svg) {
            svg.attr("version", "1.1");
            svg.attr("xmlns", d3.namespaces.svg);
            var source = new XMLSerializer().serializeToString(svg.node()),
                rect = svg.node().getBoundingClientRect();
            return {
                top: rect.top,
                left: rect.left,
                width: rect.width,
                height: rect.height,
                classes: svg.attr("class"),
                id: svg.attr("id"),
                childElementCount: svg.node().childElementCount,
                source: [source],
            };
        }

        var svg = d3.select(this.svg),
            svg_object = get_selected_svg(svg);

        svg_object.blob = new Blob(svg_object.source, {type: "text/xml"});
        return svg_object;
    }
}

export default D3Plot;
