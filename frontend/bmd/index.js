import {splitStartupRedux} from "utils/WebpackSplit";

export default function() {
    let element = document.getElementById("bmd");
    import("bmd/containers/Root").then(Component => {
        import("bmd/store/configureStore").then(store => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
}
