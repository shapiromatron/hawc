import React from 'react';
import { render } from 'react-dom';

import configureStore from 'shared/store/configureStore';

import Root from './containers/Root';

import reducer from 'nestedTagEditor/reducers';


const startup = function(){
    const store = configureStore(reducer);
    render(
       <Root store={store}/>,
       document.getElementById('root')
    );
};

export default startup;
