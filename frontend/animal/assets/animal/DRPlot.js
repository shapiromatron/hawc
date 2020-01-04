import $ from '$';
import _ from 'lodash';
import d3 from 'd3';

import D3Plot from 'utils/D3Plot';

class DRPlot extends D3Plot {
    constructor(endpoint, div, options, parent) {
        /*
         * Create a dose-response plot for a single dataset given an endpoint object
         * and the div where the object should be placed.
         */
        super(...arguments);
        this.parent = parent;
        this.options = options || { build_plot_startup: true };
        this.endpoint = endpoint;
        this.plot_div = $(div);
        this.bmd = [];
        this.set_defaults(options);
        this.get_dataset_info();
        endpoint.addObserver(this);
        if (this.options.build_plot_startup) {
            this.build_plot();
        }
    }

    update(status) {
        if (status.status === 'dose_changed') this.dose_scale_change();
    }

    dose_scale_change() {
        // get latest data from endpoint
        this.remove_bmd_lines();
        this.get_dataset_info();

        //update if plot is live
        if (this.parent && this.parent.plot === this) {
            if (this.x_axis_settings.scale_type == 'linear') {
                this.x_axis_settings.domain = [
                    this.min_x - this.max_x * this.buff,
                    this.max_x * (1 + this.buff),
                ];
            } else {
                this.x_axis_settings.domain = [this.min_x / 10, this.max_x * (1 + this.buff)];
            }
            this.x_scale = this._build_scale(this.x_axis_settings);

            this.build_x_label();
            this.add_selected_endpoint_BMD();
            this.x_axis_change_chart_update();
        }
    }

    build_plot() {
        try {
            delete this.error_bars_vertical;
            delete this.error_bars_upper;
            delete this.error_bars_lower;
            delete this.error_bar_group;
        } catch (err) {}
        this.plot_div.html('');
        this.get_plot_sizes();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.add_dr_error_bars();
        this.add_dose_response();
        this.add_selected_endpoint_BMD();
        this.render_bmd_lines();
        this.build_x_label();
        this.build_y_label();
        this.add_title();
        this.add_legend();
        this.customize_menu();

        var plot = this;
        this.y_axis_label.on('click', function(v) {
            plot.toggle_y_axis();
        });
        this.x_axis_label.on('click', function(v) {
            plot.toggle_x_axis();
        });
        this.trigger_resize();
    }

    customize_menu() {
        if (this.menu_div) {
            this.menu_div.remove();
            delete this.menu_div;
        }
        this.add_menu();
        if (this.parent) {
            this.parent.add_toggle_button(this);
        }
        var plot = this;
        var options = {
            id: 'toggle_y_axis',
            cls: 'btn btn-mini',
            title: 'Change y-axis scale (shortcut: click the y-axis label)',
            text: '',
            icon: 'icon-resize-vertical',
            on_click() {
                plot.toggle_y_axis();
            },
        };
        this.add_menu_button(options);
        options = {
            id: 'toggle_x_axis',
            cls: 'btn btn-mini',
            title: 'Change x-axis scale (shortcut: click the x-axis label)',
            text: '',
            icon: 'icon-resize-horizontal',
            on_click() {
                plot.toggle_x_axis();
            },
        };
        this.add_menu_button(options);
        if (this.endpoint.doses.length > 1) {
            options = {
                id: 'toggle_dose_units',
                cls: 'btn btn-mini',
                title: 'Change dose-units representation',
                text: '',
                icon: 'icon-certificate',
                on_click() {
                    plot.endpoint.toggle_dose_units();
                },
            };
            plot.add_menu_button(options);
        }
    }

    toggle_y_axis() {
        if (window.event && window.event.stopPropagation) event.stopPropagation();
        if (this.endpoint.data.data_type == 'C') {
            if (this.y_axis_settings.scale_type == 'linear') {
                this.y_axis_settings.scale_type = 'log';
                this.y_axis_settings.number_ticks = 1;
                var formatNumber = d3.format(',.f');
                this.y_axis_settings.label_format = formatNumber;
            } else {
                this.y_axis_settings.scale_type = 'linear';
                this.y_axis_settings.number_ticks = 10;
                this.y_axis_settings.label_format = undefined;
            }
        } else {
            var d = this.y_axis_settings.domain;
            if (d[0] === 0 && d[1] === 1) {
                this.y_axis_settings.domain = [this.min_y, this.max_y];
            } else {
                this.y_axis_settings.domain = [0, 1];
            }
        }
        this.y_scale = this._build_scale(this.y_axis_settings);
        this.y_axis_change_chart_update();
    }

    toggle_x_axis() {
        // get minimum non-zero dose and then set all control doses
        // equal to ten-times lower than the lowest dose
        if (window.event && window.event.stopPropagation) event.stopPropagation();
        if (this.x_axis_settings.scale_type == 'linear') {
            this.x_axis_settings.scale_type = 'log';
            this.x_axis_settings.number_ticks = 1;
            this.x_axis_settings.label_format = d3.format(',.f');
        } else {
            this.x_axis_settings.scale_type = 'linear';
            this.x_axis_settings.number_ticks = 5;
            this.x_axis_settings.label_format = undefined;
        }
        this._setPlottableDoseValues();
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.x_axis_change_chart_update();
    }

    _setPlottableDoseValues() {
        if (this.x_axis_settings.scale_type == 'linear') {
            this.min_x = d3.min(_.map(this.values, 'x'));
            this.x_axis_settings.domain = [
                this.min_x - this.max_x * this.buff,
                this.max_x * (1 + this.buff),
            ];
        } else {
            this.min_x = d3.min(_.map(this.values, 'x_log'));
            this.x_axis_settings.domain = [this.min_x / 10, this.max_x * (1 + this.buff)];
        }
    }

    set_defaults() {
        // Default settings for a DR plot instance
        this.line_colors = ['#BF3F34', '#545FF2', '#D9B343', '#228C5E', '#B27373']; //bmd lines
        this.padding = { top: 40, right: 20, bottom: 40, left: 60 };
        this.buff = 0.05; // addition numerical-spacing around dose/response units
        this.radius = 7;
        this.x_axis_settings = {
            scale_type: this.endpoint.defaultDoseAxis(),
            text_orient: 'bottom',
            axis_class: 'axis x_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            number_ticks: 5,
            axis_labels: true,
            label_format: undefined, //default
        };

        this.y_axis_settings = {
            scale_type: 'linear',
            text_orient: 'left',
            axis_class: 'axis y_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines y_gridlines',
            number_ticks: 6,
            axis_labels: true,
            label_format: undefined, //default
        };
    }

    get_plot_sizes() {
        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
        this.h = this.w; //plot height
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + 'px',
        });
    }

    y_axis_change_chart_update() {
        // Assuming the plot has already been constructed once,
        // rebuild plot with updated y-scale.
        var y = this.y_scale;

        //rebuild y-axis
        this.yAxis
            .scale(y)
            .ticks(this.y_axis_settings.number_ticks, this.y_axis_settings.label_format);

        this.vis
            .selectAll('.y_axis')
            .transition()
            .duration(1000)
            .call(this.yAxis);

        this.rebuild_y_gridlines({ animate: true });

        //rebuild error-bars
        this.add_dr_error_bars(true);
        this.add_dose_response(true);
        this.render_bmd_lines();
    }

    x_axis_change_chart_update() {
        // Assuming the plot has already been constructed once,
        // rebuild plot with updated x-scale.

        var x = this.x_scale;

        //rebuild x-axis
        this.xAxis
            .scale(x)
            .ticks(this.x_axis_settings.number_ticks, this.x_axis_settings.label_format);

        this.vis
            .selectAll('.x_axis')
            .transition()
            .duration(1000)
            .call(this.xAxis)
            .each('end', function() {
                //force lowest dose on axis to 0
                var vals = [];
                d3.selectAll('.x_axis text').each(function() {
                    vals.push(parseFloat($(this).text()));
                });
                var min = d3.min(vals).toString();
                var min_label = d3.selectAll('.x_axis text').filter(function() {
                    return $(this).text() === min;
                });
                min_label.text(0);
            });

        this.rebuild_x_gridlines({ animate: true });

        this.add_dr_error_bars(true);
        this.add_dose_response(true);
        this.render_bmd_lines();
    }

    get_dataset_info() {
        // Get values to be used in dose-response plots
        var ep = this.endpoint.data,
            self = this,
            values,
            sigs_data,
            dose_units = this.endpoint.dose_units;

        values = _.chain(ep.groups)
            .map(function(v, i) {
                var y,
                    cls = 'dose_points',
                    txts = ['Dose = {0} {1}'.printf(v.dose, dose_units), 'N = {0}'.printf(v.n)];

                if (ep.data_type == 'C') {
                    y = v.response;
                    txts.push(
                        'Response = {0} {1}'.printf(v.response, ep.response_units),
                        '{0} = {1}'.printf(ep.variance_name, v.variance)
                    );
                } else if (ep.data_type == 'P') {
                    y = v.response;
                    txts.push('Response = {0}'.printf(self.endpoint.get_pd_string(v)));
                } else {
                    y = v.incidence / v.n;
                    txts.push('Incidence = {0} {1}'.printf(v.incidence, ep.response_units));
                }

                if (ep.LOEL == i) cls += ' LOEL';
                if (ep.NOEL == i) cls += ' NOEL';

                return {
                    x: v.dose,
                    x_log: v.dose,
                    y,
                    cls,
                    isReported: v.isReported,
                    y_lower: v.lower_ci,
                    y_upper: v.upper_ci,
                    txt: txts.join('\n'),
                    significance_level: v.significance_level,
                };
            })
            .filter(function(d) {
                return d.isReported;
            })
            .value();

        if (values.length > 2) values[0].x_log = values[1].x_log / 10;

        sigs_data = _.chain(values)
            .filter(function(d) {
                return d.significance_level > 0;
            })
            .map(function(v) {
                return {
                    x: v.x,
                    significance_level: v.significance_level,
                    y: v.y_upper || v.y,
                };
            })
            .value();

        _.extend(this, {
            title_str: this.endpoint.data.name,
            x_label_text: 'Dose ({0})'.printf(this.endpoint.dose_units),
            y_label_text: 'Response ({0})'.printf(this.endpoint.data.response_units),
            values,
            sigs_data,
            max_x: d3.max(ep.groups, function(datum) {
                return datum.dose;
            }),
        });

        this._setPlottableDoseValues();

        if (ep.groups.length > 0) {
            var max_upper = d3.max(values, function(d) {
                    return d.y_upper || d.y;
                }),
                max_sig = d3.max(sigs_data, function(d) {
                    return d.y;
                });

            this.min_y = d3.min(values, function(d) {
                return d.y_lower || d.y;
            });
            this.max_y = d3.max([max_upper, max_sig]);
        }
    }

    add_axes() {
        // customizations for axis updates
        $.extend(this.x_axis_settings, {
            rangeRound: [0, this.w],
            x_translate: 0,
            y_translate: this.h,
        });

        $.extend(this.y_axis_settings, {
            domain: [this.min_y - this.max_y * this.buff, this.max_y * (1 + this.buff)],
            rangeRound: [this.h, 0],
            x_translate: 0,
            y_translate: 0,
        });

        this.build_x_axis();
        this.build_y_axis();
    }

    add_selected_endpoint_BMD() {
        // Update BMD lines based on dose-changes
        var self = this;
        if (
            this.endpoint.data.BMD &&
            this.endpoint.data.BMD.dose_units_id == this.endpoint.dose_units_id
        ) {
            var append = true;
            self.bmd.forEach(function(v, i) {
                if (v.BMD.id === self.endpoint.data.BMD.id) {
                    append = false;
                }
            });
            if (append) {
                this.add_bmd_line(this.endpoint.data.BMD, 'd3_bmd_selected');
            }
        }
    }

    add_dr_error_bars(update) {
        var x = this.x_scale,
            y = this.y_scale,
            hline_width = x.range()[1] * 0.02;
        this.hline_width = hline_width;

        try {
            if (!update) {
                delete this.error_bars_vertical;
                delete this.error_bars_upper;
                delete this.error_bars_lower;
                delete this.error_bar_group;
            }
        } catch (err) {}

        if (!this.error_bar_group) {
            this.error_bar_group = this.vis.append('g').attr('class', 'error_bars');
        }

        var bars = this.values.filter(function(v) {
                return $.isNumeric(v.y_lower) && $.isNumeric(v.y_upper);
            }),
            bar_options = {
                data: bars,
                x1(d) {
                    return x(d.x);
                },
                y1(d) {
                    return y(d.y_lower);
                },
                x2(d) {
                    return x(d.x);
                },
                y2(d) {
                    return y(d.y_upper);
                },
                classes: 'dr_err_bars',
                append_to: this.error_bar_group,
            };

        if (this.error_bars_vertical && update) {
            this.error_bars_vertical = this.build_line(bar_options, this.error_bars_vertical);
        } else {
            this.error_bars_vertical = this.build_line(bar_options);
        }

        $.extend(bar_options, {
            x1(d, i) {
                return x(d.x) + hline_width;
            },
            y1(d) {
                return y(d.y_lower);
            },
            x2(d, i) {
                return x(d.x) - hline_width;
            },
            y2(d) {
                return y(d.y_lower);
            },
        });
        if (this.error_bars_lower && update) {
            this.error_bars_lower = this.build_line(bar_options, this.error_bars_lower);
        } else {
            this.error_bars_lower = this.build_line(bar_options);
        }

        $.extend(bar_options, {
            y1(d) {
                return y(d.y_upper);
            },
            y2(d) {
                return y(d.y_upper);
            },
        });
        if (this.error_bars_upper && update) {
            this.error_bars_upper = this.build_line(bar_options, this.error_bars_upper);
        } else {
            this.error_bars_upper = this.build_line(bar_options);
        }
    }

    add_dose_response(update) {
        // update or create dose-response dots and labels
        var x = this.x_scale,
            y = this.y_scale;

        if (this.dots && update) {
            this.dots
                .data(this.values)
                .transition()
                .duration(1000)
                .attr('transform', (d) => `translate(${x(d.x)},${y(d.y)})`);

            this.sigs
                .data(this.sigs_data)
                .transition()
                .duration(1000)
                .attr('x', function(d) {
                    return x(d.x);
                })
                .attr('y', function(d) {
                    return y(d.y);
                });
        } else {
            var dots_group = this.vis.append('g').attr('class', 'dr_dots');

            this.dots = dots_group
                .selectAll('path.dot')
                .data(this.values)
                .enter()
                .append('circle')
                .attr('r', this.radius)
                .attr('class', function(d) {
                    return d.cls;
                })
                .attr('transform', (d) => `translate(${x(d.x)},${y(d.y)})`);

            this.dot_labels = this.dots.append('svg:title').text(function(d) {
                return d.txt;
            });

            var sigs_group = this.vis.append('g');

            this.sigs = sigs_group
                .selectAll('text')
                .data(this.sigs_data)
                .enter()
                .append('svg:text')
                .attr('x', function(d) {
                    return x(d.x);
                })
                .attr('y', function(d) {
                    return y(d.y);
                })
                .attr('text-anchor', 'middle')
                .style({
                    'font-size': '18px',
                    'font-weight': 'bold',
                    cursor: 'pointer',
                })
                .text('*');

            this.sigs_labels = this.sigs.append('svg:title').text(function(d) {
                return 'Statistically significant at {0}'.printf(d.significance_level);
            });
        }
    }

    clear_legend() {
        //remove existing legend
        $($(this.legend)[0]).remove();
        $(this.plot_div.find('.legend_circle')).remove();
        $(this.plot_div.find('.legend_text')).remove();
    }

    add_legend() {
        // clear any existing legends
        this.clear_legend();

        var legend_settings = {};
        legend_settings.items = [
            {
                text: 'Doses in Study',
                classes: 'dose_points',
                color: undefined,
            },
        ];
        if (this.plot_div.find('.LOEL').length > 0) {
            legend_settings.items.push({
                text: this.endpoint.data.noel_names.loel,
                classes: 'dose_points LOEL',
                color: undefined,
            });
        }
        if (this.plot_div.find('.NOEL').length > 0) {
            legend_settings.items.push({
                text: this.endpoint.data.noel_names.noel,
                classes: 'dose_points NOEL',
                color: undefined,
            });
        }
        var doseUnits = parseInt(this.endpoint.dose_units_id);
        this.bmd
            .filter(function(d) {
                return d.dose_units_id === doseUnits;
            })
            .forEach(function(d) {
                legend_settings.items.push({
                    text: d.name,
                    classes: '',
                    color: d.stroke,
                });
            });

        legend_settings.item_height = 20;
        legend_settings.box_w = 110;
        legend_settings.box_h = legend_settings.items.length * legend_settings.item_height;

        legend_settings.box_padding = 5;
        legend_settings.dot_r = 5;

        if (this.legend_left) {
            legend_settings.box_l = this.legend_left;
        } else {
            legend_settings.box_l = this.w - legend_settings.box_w - 10;
        }

        if (this.legend_top) {
            legend_settings.box_t = this.legend_top;
        } else if (this.endpoint.data.dataset_increasing) {
            legend_settings.box_t = this.h - legend_settings.box_h - 20;
        } else {
            legend_settings.box_t = 10;
        }

        //add final rectangle around plot
        this.add_final_rectangle();

        // build legend
        this.build_legend(legend_settings);
    }

    cleanup_before_change() {
        this.remove_bmd_lines();
    }

    add_bmd_line(line) {
        this.bmd.push(line);
        this.render_bmd_lines();
    }

    remove_bmd_line(model_id) {
        this.bmd = _.reject(this.bmd, function(d) {
            return d.id === model_id;
        });
        this.render_bmd_lines();
    }

    render_bmd_lines() {
        this.remove_bmd_lines();

        var doseUnits = parseInt(this.endpoint.dose_units_id),
            lines = this.bmd.filter(function(d) {
                return d.dose_units_id === doseUnits;
            }),
            x = this.x_scale,
            xs = this.x_scale.ticks(100),
            y = this.y_scale,
            liner = d3.svg
                .line()
                .x(function(d) {
                    return x(d.x);
                })
                .y(function(d) {
                    return y(d.y);
                })
                .interpolate('linear');

        var bmds = _.chain(lines)
            .filter(function(d) {
                return d.bmd_line !== undefined;
            })
            .map(function(d) {
                return [
                    {
                        x1: x(d.bmd_line.x),
                        x2: x(d.bmd_line.x),
                        y1: y.range()[0],
                        y2: y(d.bmd_line.y),
                        stroke: d.stroke,
                    },
                    {
                        x1: x.range()[0],
                        x2: x(d.bmd_line.x),
                        y1: y(d.bmd_line.y),
                        y2: y(d.bmd_line.y),
                        stroke: d.stroke,
                    },
                ];
            })
            .flattenDeep()
            .value();

        var bmdls = _.chain(lines)
            .filter(function(d) {
                return d.bmdl_line !== undefined;
            })
            .map(function(d) {
                return [
                    {
                        x1: x(d.bmdl_line.x),
                        x2: x(d.bmdl_line.x),
                        y1: y.range()[0],
                        y2: y(d.bmdl_line.y),
                        stroke: d.stroke,
                    },
                    {
                        x1: x.range()[0],
                        x2: x(d.bmdl_line.x),
                        y1: y(d.bmdl_line.y),
                        y2: y(d.bmdl_line.y),
                        stroke: d.stroke,
                    },
                ];
            })
            .flattenDeep()
            .value();

        var g = this.vis.append('g').attr('class', 'bmd');

        // add lines
        g
            .selectAll('path')
            .data(lines)
            .enter()
            .append('path')
            .attr('class', 'bmd_line')
            .attr('d', function(d) {
                return liner(d.getData(xs));
            })
            .attr('stroke', function(d) {
                return d.stroke;
            });

        // add bmd lines
        g
            .selectAll('line.bmd')
            .data(bmds)
            .enter()
            .append('line')
            .attr('class', 'bmd_line')
            .attr('x1', function(d) {
                return d.x1;
            })
            .attr('x2', function(d) {
                return d.x2;
            })
            .attr('y1', function(d) {
                return d.y1;
            })
            .attr('y2', function(d) {
                return d.y2;
            })
            .attr('stroke', function(d) {
                return d.stroke;
            });

        // add bmdl lines
        g
            .selectAll('line.bmd')
            .data(bmdls)
            .enter()
            .append('line')
            .attr('class', 'bmd_line')
            .attr('x1', function(d) {
                return d.x1;
            })
            .attr('x2', function(d) {
                return d.x2;
            })
            .attr('y1', function(d) {
                return d.y1;
            })
            .attr('y2', function(d) {
                return d.y2;
            })
            .attr('stroke', function(d) {
                return d.stroke;
            });

        this.add_legend();
    }

    remove_bmd_lines() {
        this.vis.selectAll('g.bmd').remove();
    }
}

export default DRPlot;
