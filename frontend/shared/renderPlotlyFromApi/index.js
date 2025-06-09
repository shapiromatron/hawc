import React from "react";
import ReactDOM from "react-dom";

import PlotFromUrl from "../components/PlotFromUrl";

export default function (el, url) {
    ReactDOM.render(<PlotFromUrl url={url} />, el);
}
