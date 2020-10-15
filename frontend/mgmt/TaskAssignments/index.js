import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import RootStore from "./stores";
import RobRoot from "./containers/RobRoot";
// import TaskRoot from "./containers/TaskRoot";

export default function(el, config) {
    const store = new RootStore(config);
    ReactDOM.render(
        <Provider store={store} robStore={store.rob} taskStore={store.task}>
            {/* <TaskRoot /> */}
            <RobRoot />
        </Provider>,
        el
    );
}
