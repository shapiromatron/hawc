import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchStudies } from 'robScoreCleanup/actions';
import h from 'shared/utils/helpers';


class Root extends Component {

    constructor(props) {
        super(props);
        this.props.store.dispatch(loadConfig());
        this.state = this.props.store.getState();
    }

    componentWillMount(){
        this.props.store.dispatch(fetchStudies());
    }

    render() {
        console.log('this.props', this.props);
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
