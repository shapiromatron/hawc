import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import {TextCleanupStore} from "./stores";
import App from "./App";

export default function(el, config) {
    const store = new TextCleanupStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
}
