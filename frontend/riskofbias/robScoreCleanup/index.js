import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import createStore from "./store";
import Main from "./containers/Main";

export default function(el) {
    const store = createStore();
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
