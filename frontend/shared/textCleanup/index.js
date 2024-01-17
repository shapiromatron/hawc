import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import App from "./App";
import {TextCleanupStore} from "./stores";

export default function(el, config) {
    const store = new TextCleanupStore(config);
    createRoot(el).render(
        <Provider store={store}>
            <App />
        </Provider>
    );
}
