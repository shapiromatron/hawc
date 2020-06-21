import d3 from "d3";
import h from "shared/utils/helpers";
import React from "react";
import "react-tabs/style/react-tabs.css";
import {inject, observer} from "mobx-react";
import {toJS} from "mobx";
import PropTypes from "prop-types";

const renderPlot = function(el, dataset) {
    var values = dataset.map(d => d.loel).filter(d => d !== null && d > 0);

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 20, right: 30, bottom: 30, left: 30},
        width = 960 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

    var x = d3.scale
        .linear()
        .domain(d3.extent(values))
        .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var data = d3.layout.histogram().bins(x.ticks(20))(values);

    var y = d3.scale
        .linear()
        .domain(d3.extent(data))
        .range([height, 0]);

    var xAxis = d3.svg
        .axis()
        .scale(x)
        .orient("bottom");

    var svg = d3
        .select(el)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    var bar = svg
        .selectAll(".bar")
        .data(data)
        .enter()
        .append("g")
        .attr("class", "bar")
        .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`);

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x(data[0].dx) - x(0) - 1)
        .attr("height", function(d) {
            return height - y(d.y);
        })
        .attr("fill", "steelblue");

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("x", (x(data[0].dx) - x(0)) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) {
            return formatCount(d.y);
        });

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
        .attr("class", "line-class")
        .attr("style", "fill: red; fill-opacity: 0.5; stroke: black; stroke-width: 2")
        .attr("cx", d => -Math.random() * xjitter + xjitter / 2 + x(d))
        .attr("cy", 0)
        .attr("r", 0);

    /*
     * Adding refresh method to reload new data
     */
    function refresh(values) {
        // var values = d3.range(1000).map(d3.random.normal(20, 5));
        var data = d3.layout.histogram().bins(x.ticks(20))(values);

        // Reset y domain using new data
        var yMax = d3.max(data, function(d) {
            return d.length;
        });
        y.domain([0, yMax]);

        var bar = svg.selectAll(".bar").data(data);

        // Remove object with data
        bar.exit().remove();

        bar.transition()
            .duration(1000)
            .attr("transform", function(d) {
                return "translate(" + x(d.x) + "," + y(d.y) + ")";
            });

        bar.select("rect")
            .transition()
            .duration(1000)
            .attr("height", function(d) {
                return height - y(d.y);
            })
            .attr("fill", "steelblue");

        bar.select("text")
            .transition()
            .duration(1000)
            .text(function(d) {
                return formatCount(d.y);
            });

        // Remove object with data
        var items = svg.selectAll(".items").data(values);
        items.exit().remove();
        items
            .select("circle")
            .transition()
            .duration(1000)
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
