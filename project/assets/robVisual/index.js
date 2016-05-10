import React from 'react';
import { render } from 'react-dom';

import Root from 'robVisual/containers/Root';
import configureStore from 'robVisual/store/configureStore';

const startup = function(){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('rootRobFilter'));
};

export default startup;
