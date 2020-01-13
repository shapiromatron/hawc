import {splitStartupRedux} from "utils/WebpackSplit";

const startup = function(element) {
    import("mgmt/Dashboard/containers/Root").then(Component => {
        import("mgmt/Dashboard/store/configureStore").then(store => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
