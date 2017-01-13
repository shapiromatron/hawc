import React from 'react';
import { render } from 'react-dom';

const startup = function(){
    import('nestedTagEditor/containers/Root').then((Component) => {
        import('shared/store/configureStore').then((configureStore) => {
            import('nestedTagEditor/reducers').then((reducer) => {
                const store = configureStore.default(reducer.default);
                console.log('Component', Component);
                render(
                   <Component.default store={store}/>,
                   document.getElementById('root')
                );
            });
        });
    });
};

export default startup;
