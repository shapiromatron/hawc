import React from "react";
import ReactDOM from "react-dom";
import Plot from "react-plotly.js";

export default function(el, url) {
    fetch(url)
        .then(response => response.json())
        .then(json => {
            ReactDOM.render(
                <Plot
                    data={json.data}
                    layout={json.layout}
                    useResizeHandler={true}
                    style={{width: "100%", height: "100%"}}
                />,
                el
            );
        });
}
