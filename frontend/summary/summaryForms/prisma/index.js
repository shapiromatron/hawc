import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import $ from "$";

import {createPrismaStore} from "../stores";
import App from "./App";

const prismaFormAppStartup = function(el, config, djangoForm) {
    const store = createPrismaStore(config, djangoForm);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <App />
        </Provider>
    );
    $(el).fadeIn();
};

export default prismaFormAppStartup;
