import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";
import HeatmapTemplateStore from "./HeatmapTemplateStore";
import HeatmapTemplateRoot from "./HeatmapTemplateRoot";

export default function(el, config) {
    const store = new HeatmapTemplateStore(config);

    ReactDOM.render(
        <Provider store={store}>
            <HeatmapTemplateRoot />
        </Provider>,
        el
    );
}
