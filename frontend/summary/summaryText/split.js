import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Root from "./Root";
import SummaryTextStore from "./store";

export default function(el, config) {
    const store = new SummaryTextStore(el, config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
