import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {createExploratoryHeatmapStore} from "../stores";
import App from "./App";

const exploratoryHeatmapFormAppStartup = function (el, config, djangoForm) {
    const store = createExploratoryHeatmapStore(config, djangoForm);
    store.subclass.getDatasetOptions();
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
    $(el).fadeIn();
};

export default exploratoryHeatmapFormAppStartup;
