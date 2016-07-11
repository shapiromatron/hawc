import React from 'react';
import { render } from 'react-dom';

import Root from 'textCleanup/containers/Root';
import configureStore from 'textCleanup/store/configureStore';

const startup = function(){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('root'));
};

export default startup;
