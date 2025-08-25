import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import Root from "./Root";
import SummaryTableEditStore from "./store";

export default function (el, config) {
    const store = new SummaryTableEditStore(config);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <Root />
        </Provider>
    );
}
