import Endpoint from "animal/Endpoint";
import * as d3 from "d3";
import _ from "lodash";
import {autorun, toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import bindTooltip from "shared/components/Tooltip";
import h from "shared/utils/helpers";

import $ from "$";

import Tooltip from "./Tooltip";

const dodgeLogarithmic = (data, x, radius, options) => {
        // https://observablehq.com/@d3/beeswarm-ii
        // https://observablehq.com/@d3/beeswarm-iii
        // modified to mutate data instead of creating a copy data
        const radius2 = radius ** 2,
            xJitter = d3.randomNormal(0, radius * 1.5), // equally space
            epsilon = 1e-3;

        let head = null,
            tail = null;

        data.forEach(d => {
            d.x = x(d.dose) + (options.approximateXValues ? xJitter() : 0);
        });

        data.sort((a, b) => a.x - b.x);

        // Returns true if circle ⟨x,y⟩ intersects with any circle in the queue.
        function intersects(x, y) {
            let a = head;
            while (a) {
                if (radius2 - epsilon > (a.x - x) ** 2 + (a.y - y) ** 2) {
                    return true;
                }
                a = a.next;
            }
            return false;
        }

        // Place each circle sequentially.
        for (const b of data) {
            // Remove circles from the queue that can’t intersect the new circle b.
            while (head && head.x < b.x - radius2) head = head.next;

            // Choose the minimum non-intersecting tangent.
            if (intersects(b.x, (b.y = 0))) {
                let a = head;
                b.y = Infinity;
                do {
                    let y1 = a.y + Math.sqrt(radius2 - (a.x - b.x) ** 2);
                    let y2 = a.y - Math.sqrt(radius2 - (a.x - b.x) ** 2);
                    if (Math.abs(y1) < Math.abs(b.y) && !intersects(b.x, y1)) b.y = y1;
                    if (options.twoSided) {
                        if (Math.abs(y2) < Math.abs(b.y) && !intersects(b.x, y2)) b.y = y2;
                    }
                    a = a.next;
                } while (a);
            }

            // Add b to the queue.
            b.next = null;
            if (head === null) head = tail = b;
            else tail = tail.next = b;
        }
    },
    renderPlot = function (el, store) {
        // always start fresh
        $(el).empty();

        const margin = {top: 20, right: 100, bottom: 30, left: 30},
            width = Math.max($(el).width(), 800) - margin.left - margin.right,
            height =
                Math.min(
                    600,
                    Math.max(
                        window.innerHeight -
                            el.getBoundingClientRect().top -
                            margin.top -
                            margin.bottom,
                        400
                    )
                ) -
                margin.top -
                margin.bottom,
            itemRadius = 5,
            fullDataset = toJS(store.plotData);

        // init full dataset
        fullDataset.forEach((d, i) => {
            d.idx = i;
            d.x = null;
            d.y = null;
            d.next = null;
        });

        let xExtent = d3.extent(fullDataset, d => d.dose),
            xFloor = 10 ** Math.floor(Math.log10(xExtent[0])),
            xCeil = 10 ** Math.ceil(Math.log10(xExtent[1])),
            x = d3.scaleLog().domain([xFloor, xCeil]).range([0, width]),
            yBaseMaxRange = height - itemRadius - 2,
            y = d3.scaleLinear().range([yBaseMaxRange, 0]);

        // hard code values for consistency, taken from `d3.schemeCategory10`
        let colorScale = d3
                .scaleOrdinal()
                .domain(["noel", "loel", "fel", "bmd", "bmdl"])
                .range(["#ff7f0e", "#1f77b4", "#d62728", "#2ca02c", "#9467bd"]),
            numTicks = Math.ceil(Math.log10(xExtent[1])) - Math.floor(Math.log10(xExtent[0])),
            xAxis = d3.axisBottom(x).ticks(numTicks + 1, ","),
            $tooltip = $("<div>").appendTo(el);

        let svg = d3
                .select(el)
                .append("svg")
                .attr("role", "image")
                .attr("aria-label", "A dose-response plot")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`),
            itemsGroup = svg.append("g").attr("class", "items");

        // draw x-axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0,${height})`)
            .call(xAxis);

        const refresh = function (settings) {
                const filterDataset = function () {
                        const filtered = fullDataset
                                .filter(d => _.includes(settings.doses, d.data["dose units id"]))
                                .filter(d => _.includes(settings.systems, d.data.system))
                                .filter(d => _.includes(settings.criticalValues, d.type)),
                            grouped = h.groupNest(filtered, d => d.data.system);

                        return _.values(grouped);
                    },
                    t = svg.transition();

                let range,
                    filteredData = filterDataset(),
                    maxYRange = 0;

                // get max range for each group to determine spacing
                _.each(filteredData, d => {
                    dodgeLogarithmic(d.values, x, itemRadius, {
                        approximateXValues: settings.approximateXValues,
                        twoSided: true,
                    });
                    range = d3.extent(d.values, el => el.y);
                    if (range[1] - range[0] > maxYRange) {
                        maxYRange = Math.ceil(range[1] - range[0]);
                    }
                });

                let systems = _.chain(filteredData)
                        .map(d => {
                            return {name: d.key, median: d3.mean(d.values, el => el.dose)};
                        })
                        .sortBy(d => d.median)
                        .value(),
                    yGroupScale = d3
                        .scalePoint()
                        .domain(systems.map(d => d.name))
                        .range([0, systems.length * maxYRange * 1.2])
                        .padding(0.3);

                _.each(filteredData, d => {
                    let addition = yGroupScale(d.key);
                    _.each(d.values, el => (el.y = el.y + addition));
                });

                // Reset y domain using new data
                let maxY = systems.length * maxYRange * 1.2;
                y.domain([0, maxY]);
                yGroupScale.range([yBaseMaxRange, 0]);

                filteredData = _.flatten(_.map(filteredData, "values"));

                itemsGroup
                    .selectAll(".critical-dose-group-g")
                    .data(systems, d => d.name)
                    .join(
                        enter => {
                            let g = enter
                                .append("g")
                                .attr("class", "critical-dose-group-g")
                                .attr("transform", d => `translate(0,${yGroupScale(d.name)})`);
                            g.append("line")
                                .attr("x1", x.range()[0])
                                .attr("x2", x.range()[1])
                                .attr("y1", 0)
                                .attr("y2", 0)
                                .attr("class", "critical-dose-group-line");
                            g.append("line")
                                .attr("x1", d => x(d.median))
                                .attr("x2", d => x(d.median))
                                .attr("y1", -10)
                                .attr("y2", 10)
                                .attr("class", "critical-dose-group-line")
                                .append("title")
                                .text(d => d.median);
                            g.append("text")
                                .attr("class", "critical-dose-legend-text")
                                .attr("x", x.range()[0])
                                .attr("y", 0)
                                .text(d => d.name || h.nullString);
                        },
                        update =>
                            update
                                .transition(t)
                                .attr("transform", d => `translate(0,${yGroupScale(d.name)})`),
                        exit =>
                            exit
                                .transition(t)
                                .style("opacity", 0)
                                .on("end", function () {
                                    d3.select(this).remove();
                                })
                    );

                // Remove object with data
                let items = itemsGroup
                    .selectAll(".critical-dose")
                    .data(filteredData, d => d.idx)
                    .join(
                        enter =>
                            enter
                                .append("circle")
                                .attr("class", "critical-dose")
                                .attr("cx", d => d.x)
                                .attr("cy", height)
                                .attr("r", 0)
                                .attr("fill", d => colorScale(d.type))
                                .on("click", (_event, d) =>
                                    Endpoint.displayAsModal(d.data["endpoint id"])
                                ),
                        update =>
                            update
                                .transition(t)
                                .delay((_d, i) => i * 2)
                                .attr("cx", d => d.x)
                                .attr("fill", d => colorScale(d.type)),
                        exit =>
                            exit
                                .transition(t)
                                .delay((_d, i) => i * 2)
                                .attr("r", 0)
                                .style("opacity", 0)
                                .on("end", function () {
                                    d3.select(this).remove();
                                })
                    );

                items
                    .transition(t)
                    .delay((_d, i) => i * 2)
                    .attr("cy", d => y(d.y))
                    .attr("r", itemRadius);

                bindTooltip($tooltip, items, (_e, d) => <Tooltip d={d} />, {
                    mouseEnterExtra: () => d3.select(event.target).moveToFront(),
                });
            },
            colorLegend = function () {
                let legend = svg
                    .append("g")
                    .attr("class", "color-legend")
                    .attr("transform", `translate(${width + 15},${15})`);

                legend
                    .append("text")
                    .attr("class", "critical-dose-legend-text")
                    .attr("style", "font-weight: bold;")
                    .attr("dx", -6)
                    .attr("dy", -15)
                    .text("Critical value");

                legend
                    .selectAll(".none")
                    .data(colorScale.domain())
                    .enter()
                    .append("g")
                    .attr("transform", (_d, i) => `translate(0,${i * 15})`)
                    .each(function (d) {
                        d3.select(this)
                            .append("circle")
                            .attr("class", "critical-dose-legend")
                            .attr("fill", colorScale(d))
                            .attr("r", itemRadius);
                        d3.select(this)
                            .append("text")
                            .attr("class", "critical-dose-legend-text")
                            .attr("dx", 10)
                            .attr("dy", 4)
                            .text(d.toUpperCase());
                    });
            };
        colorLegend();
        autorun(() => refresh(toJS(store.settings)));
    };

@inject("store")
@observer
class Plot extends React.Component {
    componentDidMount() {
        const el = document.getElementById(this.divId),
            {store} = this.props;
        renderPlot(el, store);
    }
    render() {
        this.divId = h.randomString();
        return <div id={this.divId}></div>;
    }
}
Plot.propTypes = {
    store: PropTypes.object,
};

export default Plot;
