import { splitStartupRedux } from 'utils/WebpackSplit';

const bmdStartup = function() {
    let element = document.getElementById('bmd');
    import('bmd/containers/Root').then((Component) => {
        import('bmd/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

window.app.bmdStartup = bmdStartup;

export default bmdStartup;
