import * as d3 from "d3";
import PropTypes from "prop-types";
import React from "react";
import h from "shared/utils/helpers";

const renderPlot = function(el, data) {
    const compareSets = function(data) {
            if (data.sets.length == 2) {
                const a = new Set(data.sets[0].values),
                    b = new Set(data.sets[1].values);
                return {
                    a: [...a.difference(b)],
                    b: [...b.difference(a)],
                    ab: [...a.intersection(b)],
                };
            } else if (data.sets.length == 3) {
                const a = new Set(data.sets[0].values),
                    b = new Set(data.sets[1].values),
                    c = new Set(data.sets[2].values);
                return {
                    a: [...a.difference(b).difference(c)],
                    b: [...b.difference(c).difference(a)],
                    c: [...c.difference(a).difference(b)],
                    ab: [...a.intersection(b).difference(c)],
                    bc: [...b.intersection(c).difference(a)],
                    ac: [...c.intersection(a).difference(b)],
                    abc: [...a.intersection(b).intersection(c)],
                };
            } else if (data.sets.length == 4) {
                const a = new Set(data.sets[0].values),
                    b = new Set(data.sets[1].values),
                    c = new Set(data.sets[2].values),
                    d = new Set(data.sets[3].values);
                return {
                    a: [
                        ...a
                            .difference(b)
                            .difference(c)
                            .difference(d),
                    ],
                    b: [
                        ...b
                            .difference(c)
                            .difference(d)
                            .difference(a),
                    ],
                    c: [
                        ...c
                            .difference(d)
                            .difference(a)
                            .difference(b),
                    ],
                    d: [
                        ...d
                            .difference(a)
                            .difference(b)
                            .difference(c),
                    ],
                    ab: [
                        ...a
                            .intersection(b)
                            .difference(c)
                            .difference(d),
                    ],
                    ac: [
                        ...a
                            .intersection(c)
                            .difference(b)
                            .difference(d),
                    ],
                    ad: [
                        ...a
                            .intersection(d)
                            .difference(b)
                            .difference(c),
                    ],
                    bc: [
                        ...b
                            .intersection(c)
                            .difference(d)
                            .difference(a),
                    ],
                    bd: [
                        ...b
                            .intersection(d)
                            .difference(a)
                            .difference(c),
                    ],
                    cd: [
                        ...c
                            .intersection(d)
                            .difference(a)
                            .difference(b),
                    ],
                    abc: [
                        ...a
                            .intersection(b)
                            .intersection(c)
                            .difference(d),
                    ],
                    abd: [
                        ...a
                            .intersection(b)
                            .intersection(d)
                            .difference(c),
                    ],
                    acd: [
                        ...a
                            .intersection(c)
                            .intersection(d)
                            .difference(b),
                    ],
                    bcd: [
                        ...b
                            .intersection(c)
                            .intersection(d)
                            .difference(a),
                    ],
                    abcd: [
                        ...a
                            .intersection(b)
                            .intersection(c)
                            .intersection(d),
                    ],
                };
            } else {
                return 0;
            }
        },
        make2 = function(el, width, height, labels, circles, intersections) {
            const svg = d3
                .select(el)
                .append("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "border: 1px solid #efefef;");

            svg.selectAll("text.lbl")
                .data(labels)
                .join("text")
                .attr("class", "lbl")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", d => d.anchor)
                .style("font-weight", "bold")
                .text(d => d.text);

            svg.selectAll("circle")
                .data(circles)
                .join("circle")
                .attr("cx", d => d.cx)
                .attr("cy", d => d.cy)
                .attr("r", 150)
                .attr("fill", d => d.fill)
                .attr("stroke", d => d.fill)
                .attr("stroke-width", 3)
                .style("fill-opacity", 0.3)
                .style("stroke-opacity", 0.5);

            svg.selectAll("text.intersection")
                .data(intersections)
                .join("text")
                .attr("class", "intersection")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", "middle")
                .text((d, i) => d.text);
        },
        make3 = function(el, width, height, labels, circles, intersections) {
            const svg = d3
                .select(el)
                .append("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "border: 1px solid #efefef;");
            svg.selectAll("text.lbl")
                .data(labels)
                .join("text")
                .attr("class", "lbl")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", d => d.anchor)
                .style("font-weight", "bold")
                .text(d => d.text);
            svg.selectAll("circle")
                .data(circles)
                .join("circle")
                .attr("cx", d => d.cx)
                .attr("cy", d => d.cy)
                .attr("r", 120)
                .attr("fill", d => d.fill)
                .attr("stroke", d => d.fill)
                .attr("stroke-width", 3)
                .style("fill-opacity", 0.3)
                .style("stroke-opacity", 0.5);
            svg.selectAll("text.intersection")
                .data(intersections)
                .join("text")
                .attr("class", "intersection")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", "middle")
                .text((d, i) => d.text);
        },
        make4 = function(el, height, width, labels, ellipses, intersections) {
            const svg = d3
                .select(el)
                .append("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "border: 1px solid #efefef;");
            svg.selectAll("text.lbl")
                .data(labels)
                .join("text")
                .attr("class", "lbl")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", d => d.anchor)
                .style("font-weight", "bold")
                .text(d => d.text);

            svg.selectAll("ellipses")
                .data(ellipses)
                .join("ellipse")
                .attr("cx", d => d.cx)
                .attr("cy", d => d.cy)
                .attr("rx", d => d.rx)
                .attr("ry", d => d.ry)
                .attr("transform", d => d.t)
                .attr("fill", d => d.fill)
                .attr("stroke", d => d.fill)
                .attr("stroke-width", 3)
                .style("fill-opacity", 0.3)
                .style("stroke-opacity", 0.5);

            svg.selectAll("text.intersection")
                .data(intersections)
                .join("text")
                .attr("class", "intersection")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .style("text-anchor", "middle")
                .text((d, i) => d.text)
                .append("svg:title")
                .text(d => d.hover);
        };

    const sets = compareSets(data),
        nSets = data.sets.length,
        width = 600,
        height = 400;

    if (nSets === 2) {
        const labels = [
                {x: 120, y: 70, text: data.sets[0].name, anchor: "end"},
                {x: 470, y: 70, text: data.sets[1].name, anchor: "start"},
            ],
            circles = [
                {cx: 200, cy: 220, fill: "red"},
                {cx: 400, cy: 220, fill: "blue"},
            ],
            intersections = [
                {x: 180, y: 220, text: sets.a.length},
                {x: 300, y: 220, text: sets.ab.length},
                {x: 420, y: 220, text: sets.b.length},
            ];
        make2(el, width, height, labels, circles, intersections);
    } else if (nSets === 3) {
        const labels = [
                {x: 410, y: 70, text: data.sets[0].name, anchor: "start"},
                {x: 130, y: 350, text: data.sets[1].name, anchor: "end"},
                {x: 470, y: 350, text: data.sets[2].name, anchor: "start"},
            ],
            circles = [
                {cx: 230, cy: 265, fill: "red"},
                {cx: 370, cy: 265, fill: "green"},
                {cx: 300, cy: 135, fill: "blue"},
            ],
            intersections = [
                {x: 300, y: 95, text: sets.a.length},
                {x: 185, y: 310, text: sets.b.length},
                {x: 415, y: 310, text: sets.c.length},
                {x: 300, y: 225, text: sets.abc.length},
                {x: 245, y: 190, text: sets.ab.length},
                {x: 355, y: 190, text: sets.ac.length},
                {x: 300, y: 300, text: sets.bc.length},
            ];
        make3(el, width, height, labels, circles, intersections);
    } else if (nSets === 4) {
        const labels = [
                {x: 160, y: 40, text: data.sets[0].name, anchor: "middle"},
                {x: 430, y: 40, text: data.sets[1].name, anchor: "middle"},
                {x: 140, y: 330, text: data.sets[2].name, anchor: "end"},
                {x: 455, y: 330, text: data.sets[3].name, anchor: "start"},
            ],
            ellipses = [
                {
                    cx: 305,
                    cy: 195,
                    rx: 110,
                    ry: 180,
                    t: "rotate(-50, 305, 195)",
                    fill: "orange",
                },
                {
                    cx: 295,
                    cy: 195,
                    rx: 110,
                    ry: 180,
                    t: "rotate( 50, 295, 195)",
                    fill: "green",
                },

                {
                    cx: 230,
                    cy: 230,
                    rx: 110,
                    ry: 180,
                    t: "rotate(-50, 230, 230)",
                    fill: "red",
                },
                {
                    cx: 370,
                    cy: 230,
                    rx: 110,
                    ry: 180,
                    t: "rotate( 50, 370, 230)",
                    fill: "blue",
                },
            ],
            intersections = [
                {x: 230, y: 80, text: sets.a.length, hover: "a"},
                {x: 370, y: 80, text: sets.b.length, hover: "b"},
                {x: 120, y: 190, text: sets.c.length, hover: "c"},
                {x: 480, y: 190, text: sets.d.length, hover: "d"},
                {x: 300, y: 110, text: sets.ab.length, hover: "ab"},
                {x: 180, y: 120, text: sets.ac.length, hover: "ac"},
                {x: 420, y: 280, text: sets.ad.length, hover: "ad"},
                {x: 300, y: 360, text: sets.cd.length, hover: "cd"},
                {x: 180, y: 280, text: sets.bc.length, hover: "bc"},
                {x: 415, y: 120, text: sets.bd.length, hover: "bd"},
                {x: 220, y: 180, text: sets.abc.length, hover: "abc"},
                {x: 380, y: 180, text: sets.abd.length, hover: "abd"},
                {x: 250, y: 320, text: sets.acd.length, hover: "acd"},
                {x: 350, y: 320, text: sets.bcd.length, hover: "bcd"},
                {x: 300, y: 250, text: sets.abcd.length, hover: "abcd"},
            ];
        make4(el, height, width, labels, ellipses, intersections);
    } else {
        throw new Error("Too many sets.");
    }
};

class Venn extends React.Component {
    componentDidMount() {
        const el = document.getElementById(this.divId);
        renderPlot(el, this.props.data);
    }
    render() {
        this.divId = h.randomString();
        return <div id={this.divId}></div>;
    }
}
Venn.propTypes = {
    data: PropTypes.object.isRequired,
};

export default Venn;
