import React, { Component } from 'react';
import { connect } from 'react-redux';

import { selectStudyType } from 'riskofbias/robScoreCleanup/actions/StudyTypes';
import h from 'riskofbias/robScoreCleanup/utils/helpers';

class StudyTypeSelect extends Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange({ target: { options } }) {
        let values = [...options]
            .filter(option => option.selected)
            .map(option => option.value);
        this.props.dispatch(selectStudyType(values));
    }

    render() {
        return (
            <div>
                <label className="control-label">
                    Study Type filter (optional):
                </label>
                <select
                    multiple
                    name="studyType_filter"
                    id="studyType_filter"
                    onChange={this.handleChange}
                    style={{ height: '120px' }}
                >
                    {_.map(this.props.choices, (type, i) => {
                        return (
                            <option key={i} value={type}>
                                {h.caseToWords(type)}
                            </option>
                        );
                    })}
                </select>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        isLoaded: state.studyTypes.isLoaded,
        choices: state.studyTypes.items,
    };
}

export default connect(mapStateToProps)(StudyTypeSelect);
