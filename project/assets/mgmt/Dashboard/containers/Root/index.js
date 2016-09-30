import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import UnderConstruction from 'mgmt/Dashboard/components/UnderConstruction';

class Root extends Component {

    componentWillMount() {
        this.props.dispatch(loadConfig());
    }

    render() {
        return (
            <div>
                <UnderConstruction />
            </div>
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
