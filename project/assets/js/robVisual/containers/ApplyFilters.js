import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

class ApplyFilters extends Component {
    handleSubmit(e){
        e.preventDefault();
        let { threshold, studies } = this.props,
            studyIds = _.chain(studies)
                        .filter((study) => { return study.qualities__score__sum >= threshold; })
                        .pluck('id')
                        .value();
    }

    render(){
        return (
            <div>
                <button type='button' className='btn btn-primary' onClick={this.handleSubmit.bind(this)}>Apply filters</button>
                <p className='help-block'>
                    Can't really be live, but if they press this button it refilters.
                    It should select all the effect values as an array in the state,
                    and then pass them using the `effect` parameter in the ajax call.
                    Then, based on the study-quality value on the slider, get a list
                    of study_ids and put in the `study_id`. Should then return a list
                    of enpdoints, or throw an error if the values are too large.
                </p>
                <strong>Example possible valid call:</strong>
                <ul>
                    <li><a href='/ani/api/endpoint/rob_filter/?assessment_id=126&effect[]=other'>By effect</a></li>
                    <li><a href='/ani/api/endpoint/rob_filter/?assessment_id=126&study_id[]=52469&study_id[]=52471'>By study ids</a></li>
                </ul>
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
