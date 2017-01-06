import React from 'react';
import { render } from 'react-dom';

const startup = function(){
    System.import('./containers/Root').then((Component) => {
        System.import('shared/store/configureStore').then((configureStore) => {
            System.import('nestedTagEditor/reducers').then((reducer) => {
                const store = configureStore.default(reducer.default);
                render(
                   <Component.default store={store}/>,
                   document.getElementById('root')
                );
            });
        });
    });
};

export default startup;
