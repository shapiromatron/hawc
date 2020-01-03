import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';

import { fetchAssessment } from 'textCleanup/actions/Assessment';
import Assessment from 'textCleanup/components/Assessment';
import Loading from 'shared/components/Loading';

class App extends Component {
    componentWillMount() {
        this.props.dispatch(fetchAssessment());
    }

    render() {
        let { assessment } = this.props,
            helpText =
                'After data has been initially extracted, this module can be\
                        used to update and standardize text which was used during\
                        data extraction.';
        if (_.isEmpty(assessment)) return <Loading />;
        return (
            <div>
                <Assessment assessment={assessment} helpText={helpText} />
            </div>
        );
    }
}
function mapStateToProps(state) {
    return {
        assessment: state.assessment.active,
    };
}
export default connect(mapStateToProps)(App);
