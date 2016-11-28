import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';

import Root from './containers/Root';
import configureStore from './store/configureStore';

const startup = function(element){
    const store = configureStore();
    render(<Provider store={store}><Root /></Provider>, element);
};

export default startup;
