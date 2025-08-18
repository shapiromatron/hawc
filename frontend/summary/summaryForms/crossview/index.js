import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {createCrossviewStore} from "../stores";
import App from "./App";

const startup = function (el, config, djangoForm) {
    const store = createCrossviewStore(config, djangoForm);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
    $(el).fadeIn();
};

export default startup;
