import $ from "$";
import d3 from "d3";
import h from "shared/utils/helpers";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";
import PropTypes from "prop-types";

import Endpoint from "animal/Endpoint";
import bindTooltip from "shared/components/Tooltip";

class Tooltip extends Component {
    render() {
        const {d} = this.props;
        return (
            <div style={{minWidth: 300, minHeight: 100}}>
                <p>
                    <b>{d["study citation"]}</b>
                </p>
                <p>{d["endpoint name"]}</p>
                <p>{d["system"]}</p>
                <p>{d["organ"]}</p>
                <p>{d["effect"]}</p>
                <p>{d["effect subtype"]}</p>
                <p>
                    Dose value: {d.loel} {d["dose units name"]}.
                </p>
            </div>
        );
    }
}
Tooltip.propTypes = {
    d: PropTypes.object.isRequired,
};

const renderPlot = function(el, dataset) {
    var values = dataset.filter(d => d.loel !== null && d.loel > 0);

    var margin = {top: 20, right: 30, bottom: 30, left: 30},
        width = 960 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

    var x = d3.scale
        .linear()
        .domain(d3.extent(values, d => d.loel))
        .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var data = d3.layout.histogram().bins(x.ticks(20))(values, d => d.loel);

    var y = d3.scale
        .linear()
        .domain(d3.extent(data))
        .range([height, 0]);

    var xAxis = d3.svg
        .axis()
        .scale(x)
        .orient("bottom");

    var $tooltip = $("<div>").appendTo(el);

    var svg = d3
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

    var items = svg
        .selectAll(".items")
        .data(values)
        .enter()
        .append("g")
        .attr("class", "items");

    let xjitter = width / 100,
        yjitter = height / 10;

    items
        .append("circle")
        .attr("class", "dose_points")
        .attr("style", "cursor: pointer; opacity: 0.7")
        .attr("cx", 0)
        .attr("cy", height)
        .attr("r", 0)
        .on("mouseenter", function() {
            d3.select(this).style("opacity", 1.0);
        })
        .on("mouseout", function() {
            d3.select(this).style("opacity", 0.7);
        })
        .on("click", d => {
            Endpoint.displayAsModal(d["endpoint id"]);
        });

    bindTooltip($tooltip, items, d => <Tooltip d={d} />);

    /*
     * Adding refresh method to reload new data
     */
    function refresh(values) {
        // var values = d3.range(1000).map(d3.random.normal(20, 5));
        var data = d3.layout.histogram().bins(x.ticks(20))(values, d => d.loel);

        // Reset y domain using new data
        var yMax = d3.max(data, d => d.length);
        y.domain([0, yMax]);

        // Remove object with data
        var items = svg.selectAll(".items").data(values);
        items.exit().remove();
        items
            .select("circle")
            .transition()
            .duration(1000)
            .attr("cx", d => -Math.random() * xjitter + xjitter / 2 + x(d.loel))
            .attr("cy", d => -Math.random() * yjitter + (height - 10))
            .attr("r", 5);
    }
    refresh(values);
};

@inject("store")
@observer
class Plot extends React.Component {
    componentDidMount() {
        const el = document.getElementById(h.hashString("a"));
        renderPlot(el, toJS(this.props.store.dataset));
    }
    render() {
        return <div id={h.hashString("a")}></div>;
    }
}
Plot.propTypes = {
    store: PropTypes.object,
};

export default Plot;
