import React from 'react';
import { Provider } from 'react-redux';

import './Root.css';

import { loadConfig } from 'shared/actions/Config';

import {
    getTags,
} from 'ivEndpointCategories/actions';

import Tree from 'ivEndpointCategories/containers/Tree';


class Root extends React.Component {

    componentWillMount(){
        this.props.store.dispatch(loadConfig());
        this.props.store.dispatch(getTags());
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
