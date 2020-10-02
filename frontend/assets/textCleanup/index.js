import {splitStartupRedux} from "utils/WebpackSplit";
import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "mobx-react";

import Store from "./store/store";
import App from "./containers/App";

const textCleanupStartup1 = function(element) {
        import("textCleanup/containers/Root").then(Component => {
            import("textCleanup/store/configureStore").then(store => {
                splitStartupRedux(element, Component.default, store.default);
            });
        });
    },
    textCleanupStartup2 = function(el, config) {
        const store = new Store(config);
        ReactDOM.render(
            <Provider store={store}>
                <App />
            </Provider>,
            el
        );
    };

export {textCleanupStartup1, textCleanupStartup2};
