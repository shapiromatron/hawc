import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import Assessment from 'components/Assessment';
import Loading from 'components/Loading';

import { makeAssessmentActive } from 'actions/Assessment';

class App extends Component{

    getObject(){
        return _.findWhere(
            this.props.objects,
            {id: parseInt(this.props.params.id)}
        );
    }

    componentWillMount() {
        const { id, dispatch } = this.props;
        dispatch(makeAssessmentActive(id));
    }

    render() {
        let object = this.getObject();
        if (_.isUndefined(object)) return <Loading />;
        return (
            <Assessment object={object}/>
        );
    }
}

function mapStateToProps(state){
    return {
        id: state.config.assessment_id,
        objects: state.assessment.items,
    };
}

export default connect(mapStateToProps)(App);
