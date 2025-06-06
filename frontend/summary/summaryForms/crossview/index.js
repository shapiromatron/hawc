import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import $ from "$";

import {createCrossviewStore} from "../stores";
import App from "./App";

const startup = function(el, config, djangoForm) {
    const store = createCrossviewStore(config, djangoForm);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    $(el).fadeIn();
};

export default startup;
