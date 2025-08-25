import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import Main from "./containers/Main";
import RobCleanupStore from "./store";

export default function (el, config) {
    const store = new RobCleanupStore(config);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <Main />
        </Provider>
    );
}
