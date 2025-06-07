import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import EndpointListApp from "./EndpointListApp";
import EndpointListStore from "./EndpointListStore";

export default function (el, config) {
    const store = new EndpointListStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <EndpointListApp />
        </Provider>,
        el
    );
}
