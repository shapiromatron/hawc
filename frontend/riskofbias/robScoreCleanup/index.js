import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";

import Main from "./containers/Main";
import createStore from "./store";

export default function (el, config) {
    const store = createStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
