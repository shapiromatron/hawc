import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";
import EndpointListStore from "./EndpointListStore";
import EndpointListApp from "./EndpointListApp";

let func = function(el, config) {
    const store = new EndpointListStore(config);

    ReactDOM.render(
        <Provider store={store}>
            <EndpointListApp />
        </Provider>,
        el
    );
};
export default {func};
