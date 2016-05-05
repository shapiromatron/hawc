import React from 'react';
import { render } from 'react-dom';

import Root from 'textCleanup/containers/Root';
import configureStore from 'textCleanup/store/configureStore';

import RobRoot from 'robVisual/containers/Root';
import configureRobStore from 'robVisual/store/configureStore';


if (document.getElementById('root')){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('root'));
}

if (document.getElementById('rootRobFilter')){
    const store = configureRobStore();
    render(<RobRoot store={store}/>, document.getElementById('rootRobFilter'));
}
