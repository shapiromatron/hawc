import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import Filtering from 'robVisual/components/Filtering';
import FormFieldError from 'robVisual/components/FormFieldError';
import { fetchEndpoints, formatError, clearErrors } from 'robVisual/actions/Filter';


class ApplyFilters extends Component {

    hasNoErrors(){
        let { effects, dispatch } = this.props;
        if (effects === null) {
            dispatch(formatError('effects'));
            return false;
        }
        return true;
    }

    handleSubmit(e){
        e.preventDefault();
        let { threshold, studies, dispatch } = this.props;
        dispatch(clearErrors());
        if (this.hasNoErrors()) {
            let studyIds = _.chain(studies)
                    .filter((study) => { return study.qualities__score__sum >= threshold; })
                    .pluck('id')
                    .value();
            dispatch(fetchEndpoints(studyIds));
        }
    }

    render(){
        return (
            <div>
                <FormFieldError errors={this.props.errors} />
                <button type='button' className='btn btn-primary' onClick={this.handleSubmit.bind(this)}>Apply filters</button>
                {this.props.isFetching ? <Filtering /> : null}
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        isFetching: state.filter.isFetchingEndpoints,
        errors: state.filter.errors,
        effects: state.filter.selectedEffects,
        threshold: state.filter.robScoreThreshold,
        studies: state.filter.robScores,
    };
}

export default connect(mapStateToProps)(ApplyFilters);
