import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import RobFormStore from "./store";
import Root from "./Root";

export default function(el) {
    const store = new RobFormStore();
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
