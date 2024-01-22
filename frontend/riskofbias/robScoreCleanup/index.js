import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import Main from "./containers/Main";
import createStore from "./store";

export default function (el, config) {
    const store = createStore(config);
    createRoot(el).render(
        <Provider store={store}>
            <Main />
        </Provider>
    );
}
