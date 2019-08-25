import $ from '$';
import _ from 'lodash';
import d3 from 'd3';

import HAWCUtils from 'utils/HAWCUtils';

import D3Visualization from './D3Visualization';

class CrossviewPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.setDefaults();
    }

    static get_options(eps, fld, isLog) {
        // get options for input field;
        // should replicate processEndpoint in prototype below
        var numDG = CrossviewPlot._requiredGroups(isLog);
        return _.chain(eps)
            .filter(_.partial(CrossviewPlot._filterEndpoint, _, numDG))
            .map(CrossviewPlot._cw_filter_process[fld])
            .flattenDeep()
            .sortBy()
            .uniq()
            .value();
    }

    static _requiredGroups(isLog) {
        return isLog ? 3 : 2;
    }

    static _filterEndpoint(e, numDG) {
        // need at-least two non-zero dose-groups for visualization
        return d3.sum(_.map(e.data.groups, 'isReported')) >= numDG;
    }

    setDefaults() {
        _.extend(this, {
            x_axis_settings: {
                text_orient: 'bottom',
                axis_class: 'axis x_axis',
                gridlines: false,
                gridline_class: 'primary_gridlines x_gridlines',
                number_ticks: 10,
                axis_labels: true,
                label_format: d3.format(',.f'),
            },
            y_axis_settings: {
                scale_type: 'linear',
                text_orient: 'left',
                axis_class: 'axis y_axis',
                gridlines: false,
                gridline_class: 'primary_gridlines y_gridlines',
                number_ticks: 10,
                axis_labels: true,
                label_format: d3.format('%'),
            },
            settings: {
                tag_height: 17,
                column_padding: 5,
                filter_padding: 10,
            },
        });
    }

    render($div) {
        this.plot_div = $div.html('');
        this.processData();
        if (this.dataset.length === 0) {
            return this.plot_div.html(
                '<p>Error: no endpoints found. Try selecting a different dose-unit, or changing prefilter settings.</p>'
            );
        }
        this.build_plot_skeleton(false);
        this.add_axes();
        this.draw_visualization();
        this.draw_text();
        this.build_labels();
        this.add_menu();
        this.trigger_resize();
    }

    build_labels() {
        var midX = d3.mean(this.x_scale.range()),
            midY = d3.mean(this.y_scale.range()),
            yAxisXDefault = -50,
            titleOffsetX = this.data.settings.title_x || 0,
            titleOffsetY = this.data.settings.title_y || 0,
            xAxisOffsetX = this.data.settings.xlabel_x || 0,
            xAxisOffsetY = this.data.settings.xlabel_y || 0,
            yAxisOffsetX = this.data.settings.ylabel_x || 0,
            yAxisOffsetY = this.data.settings.ylabel_y || 0,
            settings = this.data.settings;

        // add labels
        let dragTitle = this.options.dev
                ? HAWCUtils.updateDragLocationTransform((x, y) => {
                      this.data.settings.title_x = parseInt(x);
                      this.data.settings.title_y = parseInt(y);
                  })
                : function() {},
            dragX = this.options.dev
                ? HAWCUtils.updateDragLocationTransform((x, y) => {
                      this.data.settings.xlabel_x = parseInt(x);
                      this.data.settings.xlabel_y = parseInt(y);
                  })
                : function() {},
            dragY = this.options.dev
                ? d3.behavior
                      .drag()
                      .origin(Object)
                      .on('drag', function(d, i) {
                          let regexp = /\((-?[0-9]+)[, ](-?[0-9]+)\)/,
                              p = d3.select(this),
                              m = regexp.exec(p.attr('transform'));
                          if (m !== null && m.length === 3) {
                              let x = parseInt(m[1]) + parseInt(d3.event.dx),
                                  y = parseInt(m[2]) + parseInt(d3.event.dy);
                              p.attr(
                                  'transform',
                                  `translate(${x},${y}) rotate(270,${yAxisXDefault + x},${midY +
                                      y})`
                              );
                              settings.ylabel_x = x;
                              settings.ylabel_y = y;
                          }
                      })
                : function() {};

        this.vis
            .append('svg:text')
            .attr('x', midX)
            .attr('y', -10)
            .attr('transform', `translate(${titleOffsetX},${titleOffsetY})`)
            .text(this.data.settings.title)
            .attr('text-anchor', 'middle')
            .attr('class', 'dr_title')
            .attr('cursor', this.options.dev ? 'pointer' : 'default')
            .call(dragTitle);

        this.vis
            .append('svg:text')
            .attr('x', midX)
            .attr('y', d3.max(this.y_scale.range()) + 30)
            .attr('transform', `translate(${xAxisOffsetX},${xAxisOffsetY})`)
            .text(this.data.settings.xAxisLabel)
            .attr('text-anchor', 'middle')
            .attr('class', 'dr_axis_labels x_axis_label')
            .attr('cursor', this.options.dev ? 'pointer' : 'default')
            .call(dragX);

        this.vis
            .append('svg:text')
            .attr('x', yAxisXDefault)
            .attr('y', midY)
            .attr(
                'transform',
                `translate(${yAxisOffsetX},${yAxisOffsetY}) rotate(270,${yAxisXDefault +
                    yAxisOffsetX},${midY + yAxisOffsetY})`
            )
            .text(this.data.settings.yAxisLabel)
            .attr('text-anchor', 'middle')
            .attr('class', 'dr_axis_labels y_axis_label')
            .attr('cursor', this.options.dev ? 'pointer' : 'default')
            .call(dragY);
    }

    processData() {
        // create new class for each colorFilter
        if (this.data.settings.colorFilters) {
            this.data.settings.colorFilters.forEach(function(d, i) {
                d.className = '_cv_colorFilter' + i;
            });
        }

        // get filter function
        var filters_map = d3.map({
            lt(val, tgt) {
                return val < tgt;
            },
            lte(val, tgt) {
                return val <= tgt;
            },
            gt(val, tgt) {
                return val > tgt;
            },
            gte(val, tgt) {
                return val >= tgt;
            },
            contains(val, tgt) {
                if (val instanceof Array) val = val.join('|');
                val = val.toString().toLowerCase();
                tgt = tgt.toString().toLowerCase();
                return val.indexOf(tgt.toLowerCase()) > -1;
            },
            not_contains(val, tgt) {
                if (val instanceof Array) val = val.join('|').toLowerCase();
                val = val.toString().toLowerCase();
                tgt = tgt.toString().toLowerCase();
                return val.indexOf(tgt.toLowerCase()) === 1;
            },
            exact(val, tgt) {
                tgt = tgt.toString().toLowerCase();
                if (val instanceof Array) {
                    return _.chain(val)
                        .map(function(itm) {
                            return itm.toString().toLowerCase() === tgt;
                        })
                        .some()
                        .value();
                } else {
                    return val.toString().toLowerCase() === tgt;
                }
            },
        });
        if (this.data.settings.endpointFilters) {
            this.data.settings.endpointFilters.forEach(function(d) {
                d.fn = _.partial(filters_map.get(d.filterType), _, d.value);
            });
        }

        // filter endpoints
        var self = this,
            settings = this.data.settings,
            getFilters = function(d) {
                var obj = {};
                settings.filters.forEach(function(fld) {
                    obj[fld.name] = CrossviewPlot._cw_filter_process[fld.name](d);
                });
                return obj;
            },
            processEndpoint = function(e) {
                var filters = getFilters(e),
                    egFilter = settings.dose_isLog
                        ? function(eg, i) {
                              return i > 0;
                          }
                        : function(eg, i) {
                              return true;
                          },
                    classes = [],
                    stroke = settings.colorBase,
                    egs,
                    i,
                    vals;

                // apply color filters (reverse order)
                for (i = settings.colorFilters.length - 1; i >= 0; i--) {
                    let colorFilt = settings.colorFilters[i];
                    vals = CrossviewPlot._cw_filter_process[colorFilt.field](e);
                    if (self.isMatch(vals, colorFilt.value)) {
                        stroke = colorFilt.color;
                        classes.push(colorFilt.className);
                    }
                }

                egs = e.data.groups
                    .filter(egFilter)
                    .filter(function(eg) {
                        return isFinite(e._percent_change_control(eg.dose_group_id));
                    })
                    .map(function(eg) {
                        return {
                            dose: eg.dose,
                            resp: e._percent_change_control(eg.dose_group_id) / 100,
                            title: e.data.name,
                            endpoint: e,
                            filters,
                            baseStroke: stroke,
                            currentStroke: stroke,
                            classes,
                        };
                    });

                return {
                    filters,
                    plotting: egs,
                    dose_extent: d3.extent(egs, function(d) {
                        return d.dose;
                    }),
                    resp_extent: d3.extent(egs, function(d) {
                        return d.resp;
                    }),
                };
            },
            applyEndpointFilters = function(e) {
                if (settings.endpointFilterLogic.length === 0) return true;
                var val,
                    res = _.map(
                        settings.endpointFilters,
                        function(filter) {
                            val = CrossviewPlot._cw_filter_process[filter.field](e);
                            return filter.fn(val);
                        },
                        e
                    );
                return settings.endpointFilterLogic === 'and' ? _.every(res) : _.some(res);
            },
            numDG = CrossviewPlot._requiredGroups(settings.dose_isLog),
            dataset = _.chain(this.data.endpoints)
                .filter(_.partial(CrossviewPlot._filterEndpoint, _, numDG))
                .filter(applyEndpointFilters)
                .map(processEndpoint)
                .filter(function(d) {
                    return d.plotting.length > 0;
                })
                .value(),
            container_height = settings.height + 50, // menu-spacing
            dose_scale = settings.dose_isLog ? 'log' : 'linear';

        // build filters
        var filters = _.chain(settings.filters)
            .map(function(f) {
                var vals = _.chain(f.values);
                if (f.allValues) {
                    vals = _.chain(dataset)
                        .map(function(d) {
                            return d.filters[f.name];
                        })
                        .flattenDeep()
                        .sort()
                        .uniq()
                        .filter(function(d) {
                            return d != '';
                        });
                }
                return vals
                    .map(function(d) {
                        return {
                            field: f.name,
                            status: false,
                            text: d,
                            headerName: f.headerName,
                        };
                    })
                    .value();
            })
            .filter(function(d) {
                return d.length > 0;
            })
            .value();

        _.extend(this, {
            dataset,
            filters,
            active_filters: [],
            plot_settings: settings,
            w: settings.inner_width,
            h: settings.inner_height,
            dose_scale,
            padding: {
                top: settings.padding_top,
                right: settings.width - settings.padding_left - settings.inner_width,
                bottom: settings.height - settings.padding_top - settings.inner_height,
                left: settings.padding_left,
                left_original: settings.padding_left,
            },
        });
        this._set_ranges();
        this.plot_div.css({ height: '{0}px'.printf(container_height) });
    }

    _set_ranges() {
        var parseRange = function(txt) {
                var arr = txt.split(',');
                if (arr.length !== 2) return false;
                arr = _.map(arr, parseFloat);
                return _.every(_.map(arr, isFinite)) ? arr : false;
            },
            dose_range = parseRange(this.data.settings.dose_range || ''),
            resp_range = parseRange(this.data.settings.response_range || '');

        if (!dose_range) {
            dose_range = [
                d3.min(this.dataset, function(v) {
                    return v.dose_extent[0];
                }),
                d3.max(this.dataset, function(v) {
                    return v.dose_extent[1];
                }),
            ];
        }

        if (!resp_range) {
            resp_range = [
                d3.min(this.dataset, function(d) {
                    return d.resp_extent[0];
                }),
                d3.max(this.dataset, function(d) {
                    return d.resp_extent[1];
                }),
            ];
        }

        _.extend(this, {
            dose_range,
            response_range: resp_range,
        });
    }

    add_axes() {
        _.extend(this.x_axis_settings, {
            scale_type: this.dose_scale,
            domain: this.dose_range,
            rangeRound: [0, this.plot_settings.inner_width],
            x_translate: 0,
            y_translate: this.plot_settings.inner_height,
        });

        _.extend(this.y_axis_settings, {
            domain: this.response_range,
            number_ticks: 10,
            rangeRound: [this.plot_settings.inner_height, 0],
            x_translate: 0,
            y_translate: 0,
        });

        this.build_x_axis();
        this.build_y_axis();
    }

    _draw_ref_ranges() {
        var x = this.x_scale,
            y = this.y_scale,
            hrng,
            vrng,
            filter_rng = function(d) {
                return $.isNumeric(d.lower) && $.isNumeric(d.upper);
            },
            make_hrng = function(d) {
                return {
                    x: x.range()[0],
                    width: Math.abs(x.range()[1] - x.range()[0]),
                    y: y(d.upper),
                    height: Math.abs(y(d.upper) - y(d.lower)),
                    title: d.title,
                    styles: _.find(D3Visualization.styles.rectangles, {
                        name: d.style,
                    }),
                };
            },
            make_vrng = function(d) {
                return {
                    x: x(d.lower),
                    width: Math.abs(x(d.upper) - x(d.lower)),
                    y: y.range()[1],
                    height: Math.abs(y.range()[1] - y.range()[0]),
                    title: d.title,
                    styles: _.find(D3Visualization.styles.rectangles, {
                        name: d.style,
                    }),
                };
            };

        hrng = _.chain(this.plot_settings.refranges_response)
            .filter(filter_rng)
            .map(make_hrng)
            .value();

        vrng = _.chain(this.plot_settings.refranges_dose)
            .filter(filter_rng)
            .map(make_vrng)
            .value();

        hrng.push.apply(hrng, vrng);
        if (hrng.length === 0) return;

        this.g_reference_ranges = this.vis.append('g');
        this.g_reference_ranges
            .selectAll('rect')
            .data(hrng)
            .enter()
            .append('svg:rect')
            .attr('x', function(d) {
                return d.x;
            })
            .attr('y', function(d) {
                return d.y;
            })
            .attr('width', function(d) {
                return d.width;
            })
            .attr('height', function(d) {
                return d.height;
            })
            .each(function(d) {
                d3.select(this).attr(d.styles);
            });

        this.g_reference_ranges
            .selectAll('rect')
            .append('svg:title')
            .text(function(d) {
                return d.title;
            });
    }

    _draw_ref_lines() {
        var x = this.x_scale,
            y = this.y_scale,
            hrefs,
            vrefs,
            filter_ref = function(d) {
                return $.isNumeric(d.value);
            },
            make_href = function(d) {
                return {
                    x1: x.range()[0],
                    x2: x.range()[1],
                    y1: y(d.value),
                    y2: y(d.value),
                    title: d.title,
                    styles: _.find(D3Visualization.styles.lines, {
                        name: d.style,
                    }),
                };
            },
            make_vref = function(d) {
                return {
                    x1: x(d.value),
                    x2: x(d.value),
                    y1: y.range()[0],
                    y2: y.range()[1],
                    title: d.title,
                    styles: _.find(D3Visualization.styles.lines, {
                        name: d.style,
                    }),
                };
            };

        hrefs = _.chain(this.plot_settings.reflines_response)
            .filter(filter_ref)
            .map(make_href)
            .value();

        vrefs = _.chain(this.plot_settings.reflines_dose)
            .filter(filter_ref)
            .map(make_vref)
            .value();

        hrefs.push.apply(hrefs, vrefs);
        if (hrefs.length === 0) return;

        this.g_reference_lines = this.vis.append('g');
        this.g_reference_lines
            .selectAll('line')
            .data(hrefs)
            .enter()
            .append('svg:line')
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
            .each(function(d) {
                d3.select(this).attr(d.styles);
            });

        this.g_reference_lines
            .selectAll('line')
            .append('svg:title')
            .text(function(d) {
                return d.title;
            });
    }

    _draw_labels() {
        var self = this,
            drag,
            dlabels,
            labels;

        dlabels = _.map(this.plot_settings.labels, function(d) {
            d._style = _.find(D3Visualization.styles.texts, { name: d.style });
            return d;
        });

        // add labels
        if (this.options.dev) {
            drag = d3.behavior
                .drag()
                .origin(Object)
                .on('drag', function(d, i) {
                    var regexp = /\((-?[0-9]+)[, ](-?[0-9]+)\)/,
                        p = d3.select(this),
                        m = regexp.exec(p.attr('transform'));
                    if (m !== null && m.length === 3) {
                        var x = parseFloat(m[1]) + d3.event.dx,
                            y = parseFloat(m[2]) + d3.event.dy;
                        p.attr('transform', `translate(${x},${y})`);
                        self.setLabelLocation(i, x, y);
                    }
                });
        } else {
            drag = function() {};
        }

        labels = this.vis
            .append('g')
            .attr('class', 'label_holder')
            .selectAll('g.labels')
            .data(dlabels)
            .enter()
            .append('g')
            .attr('class', 'labels')
            .attr('transform', (d) => `translate(${d.x || 0},${d.y || 0})`)
            .attr('cursor', this.options.dev ? 'pointer' : 'auto')
            .call(drag)
            .each(function(d) {
                d3
                    .select(this)
                    .append('text')
                    .attr('x', 0)
                    .attr('y', 0)
                    .text(function(d) {
                        return d.caption;
                    })
                    .each(function(d) {
                        self.apply_text_styles(this, d._style);
                    })
                    .each(function(d) {
                        HAWCUtils.wrapText(this, d.max_width);
                    });
            });

        if (this.options.dev) {
            labels.each(function(d) {
                var bb = this.getBBox();
                d3
                    .select(this)
                    .insert('rect', ':first-child')
                    .attr('fill', 'orange')
                    .attr('opacity', '0.1')
                    .attr('x', bb.x)
                    .attr('y', bb.y)
                    .attr('width', bb.width)
                    .attr('height', bb.height)
                    .append('svg:title')
                    .text(function(d) {
                        return 'drag to reposition';
                    });
            });
        }
    }

    _bringColorFilterToFront(d) {
        this.vis.selectAll('.' + d.className).moveToFront();
    }

    _draw_colorFilterLabels() {
        if (!this.plot_settings.colorFilterLegend || this.plot_settings.colorFilters.length === 0)
            return;

        var self = this,
            translate = `translate(${this.plot_settings.colorFilterLegendX},${
                this.plot_settings.colorFilterLegendY
            })`,
            height = 0,
            drag = !this.options.dev
                ? function() {}
                : HAWCUtils.updateDragLocationTransform(function(x, y) {
                      self.plot_settings.colorFilterLegendX = x;
                      self.plot_settings.colorFilterLegendY = y;
                  }),
            labels,
            bb;

        labels = this.vis
            .append('g')
            .attr('class', 'colorFilterLabels')
            .attr('transform', translate)
            .call(drag);

        labels
            .append('text')
            .attr('x', 0)
            .attr('y', 0)
            .attr('text-anchor', 'start')
            .attr('class', 'crossview_title')
            .text(this.plot_settings.colorFilterLegendLabel);

        labels
            .selectAll('g.labels')
            .data(this.plot_settings.colorFilters)
            .enter()
            .append('text')
            .attr('class', 'crossview_colorFilter')
            .attr('x', 0)
            .attr('y', function(d) {
                height += 15;
                return height;
            })
            .text(function(d) {
                return d.headerName;
            })
            .style('fill', function(d) {
                return d.color;
            })
            .on('mouseover', function(d) {
                d3.select(this).style('fill', self.plot_settings.colorHover);
                self.vis
                    .selectAll('.' + d.className)
                    .style('stroke', self.plot_settings.colorHover);
                self._bringColorFilterToFront(d);
            })
            .on('mouseout', function(d) {
                d3.select(this).style('fill', d.color);
                self.vis.selectAll('.' + d.className).style('stroke', d.color);
            });

        if (this.options.dev) {
            bb = labels.node().getBBox();
            d3
                .select(labels.node())
                .insert('rect', ':first-child')
                .attr('cursor', 'pointer')
                .attr('fill', 'orange')
                .attr('opacity', '0.1')
                .attr('x', bb.x)
                .attr('y', bb.y)
                .attr('width', bb.width)
                .attr('height', bb.height)
                .append('svg:title')
                .text(function(d) {
                    return 'drag to reposition';
                });
        }
    }

    draw_visualization() {
        var x = this.x_scale,
            y = this.y_scale,
            self = this,
            paths;

        this._draw_ref_ranges();
        this._draw_ref_lines();

        // response-lines
        var response_centerlines = this.vis.append('g'),
            line = d3.svg
                .line()
                .interpolate('basis')
                .x((d) => x(d.dose))
                .y((d) => y(d.resp)),
            plotData = this.dataset.map((d) => d.plotting);

        paths = response_centerlines
            .selectAll('.crossview_paths')
            .data(plotData)
            .enter()
            .append('g')
            .attr('class', 'crossview_path_group');

        paths.each(function(d) {
            let g = d3.select(this);
            d.forEach((point) => {
                g
                    .append('circle')
                    .attr('class', 'crossview_points')
                    .attr('cx', x(point.dose))
                    .attr('cy', y(point.resp))
                    .attr('r', '6px')
                    .attr('opacity', 0)
                    .attr('fill', self.plot_settings.colorHover);
            });
            g
                .on('mouseover', function() {
                    let that = d3.select(this);
                    that.moveToFront();
                    that.selectAll('circle').style('opacity', 1);
                })
                .on('mouseout', function() {
                    d3
                        .select(this)
                        .selectAll('circle')
                        .style('opacity', 0);
                });
        });

        paths
            .append('path')
            .attr('class', (d) => `crossview_paths ${d[0].classes.join(' ')}`)
            .attr('d', line)
            .style('stroke', (d) => d[0].currentStroke)
            .on('click', (d) => d[0].endpoint.displayAsModal())
            .on('mouseover', function(d) {
                if (
                    self.active_filters.length === 0 ||
                    d[0].currentStroke === self.plot_settings.colorSelected
                ) {
                    d3.select(this).style('stroke', self.plot_settings.colorHover);
                }
                self.change_show_selected_fields(this, d, true);
            })
            .on('mouseout', function(d) {
                d3.select(this).style('stroke', d[0].currentStroke);
                self.change_show_selected_fields(this, d, false);
            })
            .append('svg:title')
            .text((d) => d[0].title);

        this._draw_labels();
        this._draw_colorFilterLabels();

        for (let i = this.plot_settings.colorFilters.length - 1; i >= 0; i--) {
            this._bringColorFilterToFront(this.plot_settings.colorFilters[i]);
        }
    }

    setFilterLocation(i, x, y) {
        _.extend(this.data.settings.filters[i], { x, y });
    }

    setLabelLocation(i, x, y) {
        _.extend(this.data.settings.labels[i], { x, y });
    }

    layout_filter(g, filters, i) {
        var self = this,
            settings = this.data.settings.filters[i],
            xOffset = this._filter_left_offset || this.settings.filter_padding,
            nPerCol = Math.ceil(filters.length / settings.columns),
            cols,
            bb,
            title,
            colg;

        cols = _.chain(filters)
            .groupBy(function(el, j) {
                return Math.floor(j / nPerCol);
            })
            .toArray()
            .value();

        // print header
        title = d3
            .select(g)
            .append('text')
            .attr('x', xOffset)
            .attr('y', -this.settings.tag_height)
            .attr('text-anchor', 'start')
            .attr('class', 'crossview_title')
            .text(filters[0].headerName);

        //build column-groups
        colg = d3
            .select(g)
            .selectAll('g.crossview_cols')
            .data(cols)
            .enter()
            .append('g')
            .attr('transform', `translate(${xOffset},0)`)
            .attr('class', 'crossview_cols');

        //layout text
        colg
            .selectAll('.crossview_fields')
            .data(function(d) {
                return d;
            })
            .enter()
            .append('text')
            .attr('x', 0)
            .attr('y', function(d, i) {
                return i * self.settings.tag_height;
            })
            .attr('text-anchor', 'start')
            .attr('class', 'crossview_fields')
            .text(function(v) {
                return v.text;
            })
            .on('click', function(v) {
                self.change_active_filters(v, this);
            })
            .on('mouseover', function(d) {
                d3.select(this).attr('fill', self.plot_settings.colorHover);
                self._update_hover_filters(d);
            })
            .on('mouseout', function(d) {
                d3.select(this).attr('fill', null);
                self._update_hover_filters();
            });

        // offset filter-column groups to prevent overlap
        colg.each(function(d) {
            d3.select(this).attr('transform', `translate(${xOffset},0)`);
            xOffset += this.getBBox().width + self.settings.column_padding;
        });

        // set offset for next filter
        bb = g.getBBox();
        this._filter_left_offset = bb.x + bb.width + this.settings.filter_padding;

        // center title-text
        if (settings.columns > 1) {
            title.attr('x', bb.x + bb.width / 2).attr('text-anchor', 'middle');
        }

        // show helper to indicate draggable
        if (self.options.dev) {
            d3
                .select(g)
                .insert('rect', ':first-child')
                .attr('fill', 'orange')
                .attr('opacity', '0.1')
                .attr('x', bb.x)
                .attr('y', bb.y)
                .attr('width', bb.width)
                .attr('height', bb.height)
                .attr('cursor', 'pointer')
                .append('svg:title')
                .text(function(d) {
                    return 'drag to reposition';
                });
        }
    }

    draw_text() {
        var self = this,
            drag = this.options.dev
                ? HAWCUtils.updateDragLocationTransform(function(x, y) {
                      self.setFilterLocation($(this).index(), x, y);
                  })
                : function() {};

        this.vis
            .append('g')
            .attr('class', 'filter_holder')
            .selectAll('g.filter')
            .data(this.filters)
            .enter()
            .append('g')
            .attr('class', 'filter')
            .attr('transform', function(d, i) {
                var x = self.data.settings.filters[i].x || 0,
                    y = self.data.settings.filters[i].y || 0;
                return `translate(${x},${y})`;
            })
            .each(function(d, i) {
                self.layout_filter(this, d, i);
            })
            .call(drag);
    }

    isMatch(val, txt) {
        // use as a filter to determine match-criteria
        return val instanceof Array ? val.indexOf(txt) >= 0 : val === txt;
    }

    change_show_selected_fields(path, v, hover_on) {
        // Highlight all filters for path currently being hovered
        var self = this,
            filterMatches = function(filter) {
                return self.isMatch(v[0].filters[filter.field], filter.text);
            };

        // IE bug with mouseover events: http://stackoverflow.com/questions/3686132/
        if (hover_on && d3.select(path).classed('crossview_path_hover')) return;

        // only show if the field is a selected subset, if selected subset exists
        if (this.path_subset && !d3.select(path).classed('crossview_selected')) return;

        d3
            .select(path)
            .classed('crossview_path_hover', hover_on)
            .moveToFront();
        d3
            .select(this.svg)
            .selectAll('.crossview_fields')
            .attr('fill', null)
            .classed('crossview_path_hover', false);

        if (hover_on) {
            d3
                .select(this.svg)
                .selectAll('.crossview_fields')
                .filter(filterMatches)
                .attr('fill', this.plot_settings.colorHover)
                .classed('crossview_path_hover', true);
        }
    }

    change_active_filters(v, text) {
        // check if filter already on; if on then turn off, else add
        var idx = this.active_filters.indexOf(v),
            isNew = idx < 0,
            color;

        if (isNew) {
            this.active_filters.push(v);
            color = this.plot_settings.colorSelected;
        } else {
            color = null;
            this.active_filters.splice(idx, 1);
        }

        d3
            .select(text)
            .classed('crossview_selected', isNew)
            .style('fill', color)
            .classed('crossview_hover', false);

        this._update_selected_filters();
    }

    _update_selected_filters() {
        // find all paths which match all selected-filters.
        var self = this,
            paths = d3.select(this.svg).selectAll('.crossview_paths');

        d3
            .select(this.svg)
            .selectAll('.crossview_paths')
            .each(function(d) {
                d[0].currentStroke = d[0].baseStroke;
            })
            .style('stroke', null)
            .classed('crossview_selected', false);
        this.path_subset = undefined;

        if (this.active_filters.length > 0) {
            this.active_filters.forEach(function(filter) {
                paths = paths.filter(function(d) {
                    return self.isMatch(d[0].filters[filter.field], filter.text);
                });
            });
            paths
                .classed('crossview_selected', true)
                .each(function(d) {
                    d[0].currentStroke = self.plot_settings.colorSelected;
                })
                .moveToFront();
            this.path_subset = paths;
        }

        this._update_hover_filters();
    }

    _update_hover_filters(hover_filter) {
        // if a hover_filter exists, toggle hover-css for selected paths
        var self = this,
            paths = this.path_subset || d3.select(this.svg).selectAll('.crossview_paths'),
            isMatching = function(d) {
                return self.isMatch(d[0].filters[hover_filter.field], hover_filter.text);
            };

        d3
            .select(this.svg)
            .selectAll('.crossview_paths')
            .style('stroke', function(d) {
                return d[0].currentStroke;
            })
            .classed('crossview_hover', false);

        if (hover_filter) {
            paths
                .filter(isMatching)
                .style('stroke', this.plot_settings.colorHover)
                .classed('crossview_hover', true)
                .moveToFront();
        }
    }
}

CrossviewPlot._filters = {
    study: 'Study',
    experiment_type: 'Experiment type',
    route_of_exposure: 'Route of exposure',
    lifestage_exposed: 'Lifestage exposed',
    species: 'Species',
    sex: 'Sex',
    generation: 'Generation',
    effects: 'Effect tags',
    system: 'System',
    organ: 'Organ',
    effect: 'Effect',
    effect_subtype: 'Effect subtype',
    monotonicity: 'Monotonicity',
    chemical: 'Chemical',
};

CrossviewPlot._cw_filter_process = {
    study(d) {
        return d.data.animal_group.experiment.study.short_citation;
    },
    experiment_type(d) {
        return d.data.animal_group.experiment.type;
    },
    route_of_exposure(d) {
        return d.data.animal_group.dosing_regime.route_of_exposure;
    },
    lifestage_exposed(d) {
        return d.data.animal_group.lifestage_exposed;
    },
    species(d) {
        return d.data.animal_group.species;
    },
    sex(d) {
        return d.data.animal_group.sex;
    },
    generation(d) {
        return d.data.animal_group.generation;
    },
    effects(d) {
        return d.data.effects.map(function(v) {
            return v.name;
        });
    },
    system(d) {
        return d.data.system;
    },
    organ(d) {
        return d.data.organ;
    },
    effect(d) {
        return d.data.effect;
    },
    effect_subtype(d) {
        return d.data.effect_subtype;
    },
    monotonicity(d) {
        return d.data.monotonicity;
    },
    chemical(d) {
        return d.data.animal_group.experiment.chemical;
    },
    endpoint_name(d) {
        return d.data.name;
    },
};

export default CrossviewPlot;
