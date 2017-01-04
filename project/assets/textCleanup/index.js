import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    System.import('textCleanup/containers/Root').then((Component) => {
        System.import('textCleanup/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
