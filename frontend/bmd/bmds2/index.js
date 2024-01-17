import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import Root from "./containers/Root";
import Bmd2Store from "./store";

export default function(el, config) {
    const store = new Bmd2Store(config);
    createRoot(el).render(
        <Provider store={store}>
            <Root />
        </Provider>
    );
}
