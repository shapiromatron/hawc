import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import $ from "$";

import {createRobStore} from "../stores";
import App from "./App";

const robFormAppStartup = function (el, config, djangoForm) {
    const store = createRobStore(config, djangoForm);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    $(el).fadeIn();
};

export default robFormAppStartup;
