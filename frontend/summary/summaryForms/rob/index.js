import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {createRobStore} from "../stores";
import App from "./App";

const robFormAppStartup = function(el, config, djangoForm) {
    const store = createRobStore(config, djangoForm);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
    $(el).fadeIn();
};

export default robFormAppStartup;
