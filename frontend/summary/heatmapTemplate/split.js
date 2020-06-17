import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";
import HeatmapTemplateStore from "./HeatmapTemplateStore";
import HeatmapTemplateRoot from "./HeatmapTemplateRoot";

let func = function(el, config) {
    const store = new HeatmapTemplateStore(config);

    ReactDOM.render(
        <Provider store={store}>
            <HeatmapTemplateRoot />
        </Provider>,
        el
    );
};
export default {
    func,
};
