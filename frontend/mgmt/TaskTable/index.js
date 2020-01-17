import {splitStartupRedux} from "utils/WebpackSplit";

const startup = function(element) {
    import("mgmt/TaskTable/containers/Root").then(Component => {
        import("mgmt/TaskTable/store/configureStore").then(store => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
