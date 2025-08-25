import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import PlotFromUrl from "../components/PlotFromUrl";

export default function (el, url) {
    const root = createRoot(el);
    root.render(<PlotFromUrl url={url} />);
}
