import { splitStartupRedux } from 'utils/WebpackSplit';

const startup = function(element) {
    import('mgmt/TaskAssignments/containers/Root').then((Component) => {
        import('mgmt/TaskAssignments/store/configureStore').then((store) => {
            splitStartupRedux(element, Component.default, store.default);
        });
    });
};

export default startup;
