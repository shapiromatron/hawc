import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import $ from "$";

import {createPrismaStore} from "../stores";
import App from "./App";

const prismaFormAppStartup = function(el, config, djangoForm) {
    const store = createPrismaStore(config, djangoForm);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
    $(el).fadeIn();
};

export default prismaFormAppStartup;
