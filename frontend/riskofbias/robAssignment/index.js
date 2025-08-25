import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import Root from "./components/Root";
import RobAssignmentStore from "./store";

export default function (el, config) {
    const store = new RobAssignmentStore(config);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <Root />
        </Provider>
    );
}
