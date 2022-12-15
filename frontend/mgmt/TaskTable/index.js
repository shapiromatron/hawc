import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Root from "./containers/Root";
import MgmtTaskTableStore from "./store";

export default function(el, config) {
    const store = new MgmtTaskTableStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
