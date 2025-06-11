import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import HeatmapTemplateRoot from "./HeatmapTemplateRoot";
import HeatmapTemplateStore from "./HeatmapTemplateStore";

export default function (el, config) {
    const store = new HeatmapTemplateStore(config);

    ReactDOM.render(
        <Provider store={store}>
            <HeatmapTemplateRoot />
        </Provider>,
        el
    );
}
