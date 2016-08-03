import React from 'react';
import { Provider } from 'react-redux';

import './Root.css';

import { loadConfig } from 'shared/actions/Config';

import {
    getTags,
} from 'nestedTagEditor/actions';

import Tree from 'nestedTagEditor/containers/Tree';


class Root extends React.Component {

    componentWillMount(){
        let {dispatch} = this.props.store;
        Promise.all([dispatch(loadConfig())])
            .then(() => dispatch(getTags()));
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <Tree />
            </Provider>
        );
    }
}

Root.propTypes = {
    store: React.PropTypes.object.isRequired,
};

export default Root;
