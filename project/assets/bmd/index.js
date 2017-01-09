import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(){
    import('bmd/containers/Root').then((Component) => {
        import('bmd/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
