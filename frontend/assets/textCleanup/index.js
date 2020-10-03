import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Store from "./store";
import App from "./App";

export default function(el, config) {
    const store = new Store(config);
    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
}
