import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import App from "./App";
import Store from "./store";

export default function(el, config) {
    const store = new Store(config);

    const root = createRoot(el);
    root.render(
        <Provider store={store}>
            <App />
        </Provider>
    );
}
