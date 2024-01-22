import {Provider} from "mobx-react";
import React from "react";
import {createRoot} from "react-dom/client";

import Main from "./components/Main";
import TagEditorStore from "./store";

export default function (el, config) {
    const store = new TagEditorStore(config);
    createRoot(el).render(
        <Provider store={store}>
            <Main />
        </Provider>
    );
}
