import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {createRobStore} from "../stores";
import App from "./App";

const robFormAppStartup = function(el, config, djangoForm) {
    const store = createRobStore(config);
    store.base.setDjangoForm(djangoForm);
    store.base.setInitialData();
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
    $(el).fadeIn();
};

export default robFormAppStartup;
