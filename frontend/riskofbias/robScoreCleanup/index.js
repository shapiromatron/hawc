import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import store from "./store";
import Main from "./containers/Main";

export default function(el) {
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
