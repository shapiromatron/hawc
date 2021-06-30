import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import h from "shared/utils/helpers";

import createStore from "./store";
import Main from "./containers/Main";

export default function(el, configEl) {
    const config = h.parseJsonFromElement(configEl),
        store = createStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
