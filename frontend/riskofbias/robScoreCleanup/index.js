import {splitStartupRedux} from "utils/WebpackSplit";

const startup = function(element) {
    import("riskofbias/robScoreCleanup/containers/Root").then(Component => {
        import("riskofbias/robScoreCleanup/store/configureStore").then(store => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
