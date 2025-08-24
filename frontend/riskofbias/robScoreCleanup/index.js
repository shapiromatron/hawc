import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Main from "./containers/Main";
import RobCleanupStore from "./store";

export default function (el, config) {
    const store = new RobCleanupStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
