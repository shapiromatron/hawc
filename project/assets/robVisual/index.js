import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    System.import('robVisual/containers/Root').then((Component) => {
        System.import('robVisual/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
