import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element) {
    import('textCleanup/containers/Root').then((Component) => {
        import('textCleanup/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
