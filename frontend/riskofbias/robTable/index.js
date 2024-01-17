import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import Root from "./containers/Root";
import RobTableStore from "./store";

export default function(el, config) {
    const store = new RobTableStore(config);
    createRoot(el).render(
        <Provider store={store}>
            <Root />
        </Provider>
    );
}
