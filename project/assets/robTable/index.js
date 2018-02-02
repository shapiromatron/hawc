import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    import('robTable/containers/Root').then((Component) => {
        import('robTable/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;