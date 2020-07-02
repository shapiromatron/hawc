import _ from "lodash";
import $ from "$";
import PropTypes from "prop-types";
import React from "react";
import * as d3 from "d3";
import {inject, observer} from "mobx-react";
import {autorun, toJS} from "mobx";

import h from "shared/utils/helpers";
import bindTooltip from "shared/components/Tooltip";
import Endpoint from "animal/Endpoint";

import Tooltip from "./Tooltip";

const dodgeLogarithmic = (data, x, radius, approximateXValues) => {
        // https://observablehq.com/@d3/beeswarm-iii
        // modified to mutate data instead of creating a copy data
        const radius2 = radius ** 2,
            xJitter = d3.randomNormal(0, radius * 1.5), // equally space
            epsilon = 1e-3;

        let head = null,
            tail = null;

        data.forEach(d => {
            d.x = x(d.dose) + (approximateXValues ? xJitter() : 0);
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
                    let y = a.y + Math.sqrt(radius2 - (a.x - b.x) ** 2);
                    if (y < b.y && !intersects(b.x, y)) b.y = y;
                    a = a.next;
                } while (a);
            }

            // Add b to the queue.
            b.next = null;
            if (head === null) head = tail = b;
            else tail = tail.next = b;
        }
    },
    renderPlot = function(el, store) {
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
            fullDataset = toJS(store.plotData),
            settings = toJS(store.settings);

        fullDataset.forEach((d, i) => {
            d.idx = i;
            d.x = null;
            d.y = null;
            d.next = null;
        });

        let xExtent = d3.extent(fullDataset, d => d.dose),
            xFloor = 10 ** Math.floor(Math.log10(xExtent[0])),
            xCeil = 10 ** Math.ceil(Math.log10(xExtent[1])),
            x = d3
                .scaleLog()
                .domain([xFloor, xCeil])
                .range([0, width]);

        dodgeLogarithmic(fullDataset, x, itemRadius, settings.approximateXValues);

        let yBaseMaxRange = height - itemRadius - 2,
            y = d3
                .scaleLinear()
                .domain(d3.extent(fullDataset.map(d => d.y)))
                .range([yBaseMaxRange, 0]);

        // hard code values for consistency
        // using d3.category10
        let colorScale = d3
            .scaleOrdinal()
            .domain(["noel", "loel", "fel", "bmd", "bmdl"])
            .range(["#ff7f0e", "#1f77b4", "#d62728", "#2ca02c", "#9467bd"]);

        let numTicks = Math.ceil(Math.log10(xExtent[1])) - Math.floor(Math.log10(xExtent[0])),
            xAxis = d3
                .axisBottom(x)
                .ticks(numTicks, ",")
                .tickSize(6, 0);

        let $tooltip = $("<div>").appendTo(el);

        let svg = d3
            .select(el)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0,${height})`)
            .call(xAxis);

        let itemsGroup = svg.append("g").attr("class", "items");

        const refresh = function(settings) {
                const filterDataset = function() {
                        return fullDataset
                            .filter(d => _.includes(settings.doses, d.data["dose units id"]))
                            .filter(d => _.includes(settings.systems, d.data.system))
                            .filter(d => _.includes(settings.criticalValues, d.type));
                    },
                    filteredData = filterDataset(),
                    t = svg.transition();

                dodgeLogarithmic(filteredData, x, itemRadius, settings.approximateXValues);

                let maxY = d3.max(filteredData, d => d.y);

                // Reset y domain using new data
                y.domain([0, Math.max(yBaseMaxRange / Math.sqrt(itemRadius), maxY)]);

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
                                .on("click", d => Endpoint.displayAsModal(d.data["endpoint id"])),
                        update =>
                            update
                                .transition(t)
                                .delay((d, i) => i * 2)
                                .attr("cx", d => d.x)
                                .attr("fill", d => colorScale(d.type)),
                        exit =>
                            exit
                                .transition(t)
                                .delay((d, i) => i * 2)
                                .attr("r", 0)
                                .style("opacity", 0)
                                .on("end", function() {
                                    d3.select(this).remove();
                                })
                    );

                items
                    .transition(t)
                    .delay((d, i) => i * 2)
                    .attr("cy", d => y(d.y))
                    .attr("r", itemRadius);

                bindTooltip($tooltip, items, d => <Tooltip d={d} />, {
                    mouseEnterExtra: () => d3.select(event.target).moveToFront(),
                });
            },
            colorLegend = function() {
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
                    .attr("transform", (d, i) => `translate(0,${i * 15})`)
                    .each(function(d) {
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
