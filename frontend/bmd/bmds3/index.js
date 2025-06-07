import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Root from "./containers/Root";
import Bmd3Store from "./store";

export default function (el, config) {
    const store = new Bmd3Store(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
