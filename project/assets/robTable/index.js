import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    System.import('robTable/containers/Root').then((Component) => {
        System.import('robTable/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
