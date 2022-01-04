import $ from "$";
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

import {Provider} from "mobx-react";
import {createExploratoryHeatmapStore} from "../stores";

const exploratoryHeatmapFormAppStartup = function(el, config, djangoForm) {
    const store = createExploratoryHeatmapStore(config);
    store.base.setInitialData();
    store.base.setDjangoForm(djangoForm);
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
