import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    import('robScoreCleanup/containers/Root').then((Component) => {
        import('robScoreCleanup/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
