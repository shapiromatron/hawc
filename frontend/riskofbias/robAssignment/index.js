import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import Root from "./components/Root";
import RobAssignmentStore from "./store";

export default function (el, config) {
    const store = new RobAssignmentStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
