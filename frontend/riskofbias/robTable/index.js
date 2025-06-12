import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import Root from "./containers/Root";
import RobTableStore from "./store";

export default function (el, config) {
    const store = new RobTableStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
