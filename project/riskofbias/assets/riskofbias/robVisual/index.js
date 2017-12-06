import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element) {
    import('riskofbias/robVisual/containers/Root').then(Component => {
        import('riskofbias/robVisual/store/configureStore').then(store => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
