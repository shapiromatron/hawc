import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element) {
    import('riskofbias/robTable/containers/Root').then((Component) => {
        import('riskofbias/robTable/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
