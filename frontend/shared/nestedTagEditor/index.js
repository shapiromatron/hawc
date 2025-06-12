import {Provider} from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import Main from "./components/Main";
import TagEditorStore from "./store";

export default function (el, config) {
    const store = new TagEditorStore(config);
    ReactDOM.render(
        <Provider store={store}>
            <Main />
        </Provider>,
        el
    );
}
