import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import RobAssignmentStore from "./store";
import Root from "./containers/Root";

export default function(el, config) {
    const store = new RobAssignmentStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Root />
        </Provider>,
        el
    );
}
