import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import App from "./App";
import {TextCleanupStore} from "./stores";

export default function (el, config) {
    const store = new TextCleanupStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
}
