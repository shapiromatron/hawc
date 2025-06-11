import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import $ from "$";

import {createExploratoryHeatmapStore} from "../stores";
import App from "./App";

const exploratoryHeatmapFormAppStartup = function (el, config, djangoForm) {
    const store = createExploratoryHeatmapStore(config, djangoForm);
    store.subclass.getDatasetOptions();
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    $(el).fadeIn();
};

export default exploratoryHeatmapFormAppStartup;
