import React from "react";
import ReactDOM from "react-dom";

import HeatmapTemplateStore from "./HeatmapTemplateStore";
import HeatmapTemplateRoot from "./HeatmapTemplateRoot";

let func = function(el, config) {
    const store = new HeatmapTemplateStore(config);
    ReactDOM.render(<HeatmapTemplateRoot store={store} />, el);
};

export default {
    func,
};
