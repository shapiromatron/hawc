import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element){
    System.import('robScoreCleanup/containers/Root').then((Component) => {
        System.import('robScoreCleanup/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
