import React from 'react';
import { render } from 'react-dom';

import Root from 'robTable/containers/Root';
import configureStore from 'robTable/store/configureStore';

const startup = function(element){
    const store = configureStore();
    render(<Root store={store}/>, element);
};

export default startup;
