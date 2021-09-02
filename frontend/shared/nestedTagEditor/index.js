import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import TagEditorStore from "./store";
import Main from "./components/Main";

export default function(el, config) {
    const store = new TagEditorStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
