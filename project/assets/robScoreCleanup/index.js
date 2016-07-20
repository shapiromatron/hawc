import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';

import Root from 'robScoreCleanup/containers/Root';
import configureStore from 'robScoreCleanup/store/configureStore';

const startup = function(element){
    const store = configureStore();
    render(<Provider store={store}><Root /></Provider>, element);
};

export default startup;
