import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import EndpointListStore from "./EndpointListStore";
import EndpointListApp from "./EndpointListApp";

export default function(el, config) {
    const store = new EndpointListStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <EndpointListApp />
        </Provider>,
        el
    );
}
