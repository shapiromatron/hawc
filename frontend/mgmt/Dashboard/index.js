import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Root from "./Root";
import MgmtDashboardStore from "./store";

export default function(el, config) {
    const store = new MgmtDashboardStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
