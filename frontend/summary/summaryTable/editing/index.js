import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Root from "./Root";
import SummaryTableEditStore from "./store";

export default function (el, config) {
    const store = new SummaryTableEditStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
