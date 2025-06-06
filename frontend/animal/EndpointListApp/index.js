import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import EndpointListApp from "./EndpointListApp";
import EndpointListStore from "./EndpointListStore";

export default function(el, config) {
    const store = new EndpointListStore(config);
    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <EndpointListApp />
        </Provider>
    );
}
