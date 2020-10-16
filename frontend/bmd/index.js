import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Bmd2Store from "./newStore";
import Root from "./containers/Root";

export default function(el, config) {
    const store = new Bmd2Store(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
