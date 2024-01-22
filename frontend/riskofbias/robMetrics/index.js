import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import Root from "./Root";
import RobMetricsStore from "./store";

export default function (el, config) {
    const store = new RobMetricsStore(config);
    createRoot(el).render(
        <Provider store={store}>
            <Root />
        </Provider>
    );
}
