import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import RobTableStore from "./store";
import Root from "./components/Root";

export default function(el, config) {
    const store = new RobTableStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
