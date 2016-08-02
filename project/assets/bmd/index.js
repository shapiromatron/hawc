import React from 'react';
import { render } from 'react-dom';

import Root from 'bmd/containers/Root';
import configureStore from 'bmd/store/configureStore';

const startup = function(){
    const store = configureStore();
    render(<Root store={store}/>, document.getElementById('bmd'));
};

export default startup;
