import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import store from "./store";
import Root from "./Root";

export default function(el) {
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
