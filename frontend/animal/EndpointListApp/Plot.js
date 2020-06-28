import _ from "lodash";
import $ from "$";
import PropTypes from "prop-types";
import React from "react";
import d3 from "d3";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";

import h from "shared/utils/helpers";
import bindTooltip from "shared/components/Tooltip";
import Endpoint from "animal/Endpoint";

import Tooltip from "./Tooltip";

const renderPlot = function(el, values) {
    const margin = {top: 20, right: 30, bottom: 30, left: 30},
        width = 960 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom,
        xjitter = width / 100,
        yjitter = height,
        valueTypes = _.chain(values)
            .map(d => d.type)
            .uniq()
            .value();

    let xExtent = d3.extent(values, d => d.dose),
        xFloor = 10 ** Math.floor(Math.log10(xExtent[0])),
        xCeil = 10 ** Math.ceil(Math.log10(xExtent[1])),
        x = d3.scale
            .log()
            .domain([xFloor, xCeil])
            .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    let data = d3.layout.histogram().bins(x.ticks(20))(values, d => d.dose);

    let y = d3.scale
        .linear()
        .domain(d3.extent(data))
        .range([height, 0]);

    // hard code values for consistency
    // using d3.category10
    let colorScale = d3.scale
        .ordinal()
        .domain(["noel", "loel", "fel", "bmd", "bmdl"])
        .range(["#ff7f0e", "#1f77b4", "#d62728", "#2ca02c", "#9467bd"]);

    let numTicks = (Math.ceil(Math.log10(xExtent[1])) - Math.floor(Math.log10(xExtent[0]))) * 2,
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
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    let items = svg
        .selectAll(".items")
        .data(values)
        .enter()
        .append("g")
        .attr("class", "items");

    items
        .append("circle")
        .attr("class", "critical-dose")
        .attr("cx", d => -Math.random() * xjitter + xjitter / 2 + x(d.dose))
        .attr("cy", height)
        .attr("r", 0)
        .attr("fill", d => colorScale(d.type))
        .on("click", d => Endpoint.displayAsModal(d["endpoint id"]));

    bindTooltip($tooltip, items, d => <Tooltip d={d} />);

    const refresh = function(values) {
            let data = d3.layout.histogram().bins(x.ticks(20))(values, d => d.dose);

            // Reset y domain using new data
            let yMax = d3.max(data, d => d.length);
            y.domain([0, yMax]);

            // Remove object with data
            let items = svg.selectAll(".items").data(values);
            items.exit().remove();
            items
                .select("circle")
                .transition()
                .delay((d, i) => i)
                .attr("cy", d => -Math.random() * yjitter + (height - 10))
                .attr("r", 6);
        },
        colorLegend = function() {
            let legend = svg
                .append("g")
                .attr("class", "color-legend")
                .attr("transform", `translate(${width - 80},${15})`);

            legend
                .append("text")
                .attr("dx", -6)
                .attr("dy", -15)
                .text("Critical value type");

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
                        .attr("r", 6);
                    d3.select(this)
                        .append("text")
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
        const el = document.getElementById(h.hashString("a"));
        renderPlot(el, toJS(this.props.store.plottingDataset));
    }
    render() {
        return <div id={h.hashString("a")}></div>;
    }
}
Plot.propTypes = {
    store: PropTypes.object,
};

export default Plot;
