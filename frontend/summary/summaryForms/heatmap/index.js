import $ from "$";
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

import {Provider} from "mobx-react";
import {createExploratoryHeatmapStore} from "../stores";

const exploratoryHeatmapFormAppStartup = function(el, config, djangoForm) {
    const store = createExploratoryHeatmapStore();
    store.base.setConfig(config);
    store.base.setDjangoForm(djangoForm);

    const Root = (
        <Provider store={store}>
            <App />
        </Provider>
    );
    ReactDOM.render(Root, el);
    $(el).fadeIn();
};

export default exploratoryHeatmapFormAppStartup;
