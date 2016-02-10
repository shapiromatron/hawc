import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import FormFieldError from 'robVisual/components/FormFieldError';
import { fetchEndpoints } from 'robVisual/actions/Filter';

class ApplyFilters extends Component {

    componentWillMount(){
        this.setState({errors: []});
    }

    handleSubmit(e){
        e.preventDefault();
        if (this.props.effects) {
            let { threshold, studies, dispatch } = this.props,
                studyIds = _.chain(studies)
                    .filter((study) => { return study.qualities__score__sum >= threshold; })
                    .pluck('id')
                    .value();
            dispatch(fetchEndpoints(studyIds));
        } else {
            this.setState({errors: [...this.state.errors, 'At least one effect must be chosen.']});
        }
    }

    render(){
        return (
            <div>
                <FormFieldError errors={this.state.errors} />
                <button type='button' className='btn btn-primary' onClick={this.handleSubmit.bind(this)}>Apply filters</button>
                <p className='help-block'>
                    Can't really be live, but if they press this button it refilters.
                    It should select all the effect values as an array in the state,
                    and then pass them using the `effect` parameter in the ajax call.
                    Then, based on the study-quality value on the slider, get a list
                    of study_ids and put in the `study_id`. Should then return a list
                    of enpdoints, or throw an error if the values are too large.
                </p>

            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        effects: state.filter.selectedEffects,
        threshold: state.filter.robScoreThreshold,
        studies: state.filter.robScores,
    };
}

export default connect(mapStateToProps)(ApplyFilters);
