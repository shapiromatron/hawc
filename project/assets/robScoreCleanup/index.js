import React from 'react';
import { render } from 'react-dom';

import Root from 'robScoreCleanup/containers/Root';
import configureStore from 'robScoreCleanup/store/configureStore';

const startup = function(element){
    const store = configureStore();
    render(<Root store={store}/>, element);
};

export default startup;
