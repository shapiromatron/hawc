import React from 'react';
import { render } from 'react-dom';

import Root from 'robTable/containers/Root';
import configureStore from 'robTable/store/configureStore';

const startup = function(){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('robTable'));
};

export default startup;
