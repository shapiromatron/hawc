import React from "react";
import {createRoot} from "react-dom/client";

import PlotFromUrl from "../components/PlotFromUrl";

export default function(el, url) {
    createRoot(el).render(<PlotFromUrl url={url} />);
}
