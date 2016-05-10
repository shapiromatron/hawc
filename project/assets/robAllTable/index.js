import React from 'react';
import { render } from 'react-dom';

import Root from 'robAllTable/containers/Root';
import configureStore from 'robAllTable/store/configureStore';

const startup = function(){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('robAllTable'));
};

export default startup;
