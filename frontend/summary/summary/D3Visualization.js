import D3Plot from "shared/utils/D3Plot";
import HAWCUtils from "shared/utils/HAWCUtils";

import {Patterns} from "./common";

class D3Visualization extends D3Plot {
    constructor(parent, data, options) {
        super();
        this.parent = parent;
        this.data = data;
        this.options = options || {};
        this.settings = {};
    }

    setDefaults() {
        return HAWCUtils.abstractMethod();
    }

    render(_$div) {
        return HAWCUtils.abstractMethod();
    }

    processData() {
        return HAWCUtils.abstractMethod();
    }
}

D3Visualization.styles = {
    lines: [
        {
            name: "base",
            stroke: "#708090",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 3,
        },
        {
            name: "reference line",
            stroke: "#000000",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.8,
            "stroke-width": 2,
        },
        {
            name: "transparent",
            stroke: "#000000",
            "stroke-dasharray": "none",
            "stroke-opacity": 0,
            "stroke-width": 0,
        },
        {
            name: "solid | black",
            stroke: "#000000",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | red",
            stroke: "#e32727",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | green",
            stroke: "#006a1e",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | blue",
            stroke: "#006dbe",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | orange",
            stroke: "#dc8f00",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | purple",
            stroke: "#b82cff",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "solid | fuschia",
            stroke: "#ab006c",
            "stroke-dasharray": "none",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | black",
            stroke: "#000000",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | red",
            stroke: "#e32727",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | green",
            stroke: "#006a1e",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | blue",
            stroke: "#006dbe",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | orange",
            stroke: "#dc8f00",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | purple",
            stroke: "#b82cff",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dashed | fuschia",
            stroke: "#ab006c",
            "stroke-dasharray": "10, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | black",
            stroke: "#000000",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | red",
            stroke: "#e32727",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | green",
            stroke: "#006a1e",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | blue",
            stroke: "#006dbe",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | orange",
            stroke: "#dc8f00",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | purple",
            stroke: "#b82cff",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dotted | fuschia",
            stroke: "#ab006c",
            "stroke-dasharray": "2, 3",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | black",
            stroke: "#000000",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | red",
            stroke: "#e32727",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | green",
            stroke: "#006a1e",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | blue",
            stroke: "#006dbe",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | orange",
            stroke: "#dc8f00",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | purple",
            stroke: "#b82cff",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
        {
            name: "dash-dotted | fuschia",
            stroke: "#ab006c",
            "stroke-dasharray": "15, 10, 5, 10",
            "stroke-opacity": 0.9,
            "stroke-width": 2,
        },
    ],
    rectangles: [
        {
            name: "base",
            fill: "#be6a62",
            "fill-opacity": 0.3,
            stroke: "#be6a62",
            "stroke-width": 1.5,
            pattern: Patterns.solid,
        },
        {
            name: "black",
            fill: "#000000",
            "fill-opacity": 0.2,
            stroke: "#000000",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "red",
            fill: "#e32727",
            "fill-opacity": 0.2,
            stroke: "#6f0000",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "green",
            fill: "#22ba53",
            "fill-opacity": 0.2,
            stroke: "#006a1e",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "blue",
            fill: "#3aa4e5",
            "fill-opacity": 0.2,
            stroke: "#006dbe",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "orange",
            fill: "#ffb100",
            "fill-opacity": 0.2,
            stroke: "#dc8f00",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "purple",
            fill: "#b82cff",
            "fill-opacity": 0.2,
            stroke: "#5e5e5e",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
        {
            name: "fuschia",
            fill: "#d4266e",
            "fill-opacity": 0.2,
            stroke: "#ab006c",
            "stroke-width": 0,
            pattern: Patterns.solid,
        },
    ],
    texts: [
        {
            name: "base",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#000",
            "fill-opacity": 1,
        },
        {
            name: "header",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "bold",
            "text-anchor": "middle",
            fill: "#000",
            "fill-opacity": 1,
        },
        {
            name: "title",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "bold",
            "text-anchor": "middle",
            fill: "#000",
            "fill-opacity": 1,
        },
        {
            name: "transparent",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#000000",
            "fill-opacity": 0,
        },
        {
            name: "normal | black",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#000000",
            "fill-opacity": 1,
        },
        {
            name: "normal | red",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#6f0000",
            "fill-opacity": 1,
        },
        {
            name: "normal | green",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#006a1e",
            "fill-opacity": 1,
        },
        {
            name: "normal | blue",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#006dbe",
            "fill-opacity": 1,
        },
        {
            name: "normal | orange",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#dc8f00",
            "fill-opacity": 1,
        },
        {
            name: "normal | purple",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#b82cff",
            "fill-opacity": 1,
        },
        {
            name: "normal | fuschia",
            "font-size": "12px",
            rotate: 0,
            "font-weight": "normal",
            "text-anchor": "start",
            fill: "#ab006c",
            "fill-opacity": 1,
        },
    ],
};

export default D3Visualization;
