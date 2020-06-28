import $ from "$";
import PropTypes from "prop-types";
import React from "react";
import d3 from "d3";
import {inject, observer} from "mobx-react";
import {autorun, toJS} from "mobx";

import h from "shared/utils/helpers";
import bindTooltip from "shared/components/Tooltip";
import Endpoint from "animal/Endpoint";

import Tooltip from "./Tooltip";

const dodgeLogarithmic = (data, x, radius) => {
        // https://observablehq.com/@d3/beeswarm-iii
        const radius2 = radius ** 2,
            circles = data.map(d => ({x: x(d.dose), data: d})).sort((a, b) => a.x - b.x),
            epsilon = 1e-3;
        let head = null,
            tail = null;

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
        for (const b of circles) {
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

        return circles;
    },
    renderPlot = function(el, values) {
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
            itemRadius = 5;

        let xExtent = d3.extent(values, d => d.dose),
            xFloor = 10 ** Math.floor(Math.log10(xExtent[0])),
            xCeil = 10 ** Math.ceil(Math.log10(xExtent[1])),
            x = d3.scale
                .log()
                .domain([xFloor, xCeil])
                .range([0, width]);

        let scaledData = dodgeLogarithmic(values, x, itemRadius);

        let yBaseMaxRange = height - itemRadius - 2,
            y = d3.scale
                .linear()
                .domain(d3.extent(scaledData.map(d => d.y)))
                .range([yBaseMaxRange, 0]);

        // hard code values for consistency
        // using d3.category10
        let colorScale = d3.scale
            .ordinal()
            .domain(["noel", "loel", "fel", "bmd", "bmdl"])
            .range(["#ff7f0e", "#1f77b4", "#d62728", "#2ca02c", "#9467bd"]);

        let numTicks = Math.ceil(Math.log10(xExtent[1])) - Math.floor(Math.log10(xExtent[0])),
            xAxis = d3.svg
                .axis()
                .scale(x)
                .orient("bottom")
                .ticks(numTicks, ",.f")
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

        let items = svg
            .selectAll(".items")
            .data(scaledData)
            .enter()
            .append("g")
            .attr("class", "items");

        items
            .append("circle")
            .attr("class", "critical-dose")
            .attr("cx", d => d.x)
            .attr("cy", height)
            .attr("r", 0)
            .attr("fill", d => colorScale(d.data.type))
            .on("mouseenter", function() {
                d3.select(this).moveToFront();
            })
            .on("click", d => Endpoint.displayAsModal(d.data.data["endpoint id"]));

        bindTooltip($tooltip, items, d => <Tooltip d={d.data} />);

        const refresh = function(values) {
                let data = dodgeLogarithmic(values, x, itemRadius),
                    maxY = d3.max(data, d => d.y);

                // Reset y domain using new data
                y.domain([0, Math.max(yBaseMaxRange / Math.sqrt(itemRadius), maxY)]);

                // Remove object with data
                let items = svg.selectAll(".items").data(data);
                items.exit().remove();
                items
                    .select("circle")
                    .transition()
                    .delay((d, i) => i)
                    .attr("cy", d => y(d.y))
                    .attr("r", itemRadius);
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
                    .selectAll(".item")
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
        refresh(values);
    };

@inject("store")
@observer
class Plot extends React.Component {
    componentDidMount() {
        const el = document.getElementById(this.divId);
        autorun(() => renderPlot(el, toJS(this.props.store.plotData)));
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
