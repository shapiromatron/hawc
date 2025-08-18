import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import App from "./App";
import Store from "./store";

export default function (el, config) {
    const store = new Store(config);

    ReactDOM.render(
        <Provider store={store}>
            <App />
        </Provider>,
        el
    );
}
