import React, { Component } from 'react';
import { connect } from 'react-redux';

import { selectScores } from 'riskofbias/robScoreCleanup/actions/Scores';

export class ScoreSelect extends Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange({ target: { options } }) {
        let values = [...options].filter(o => o.selected).map(o => o.value);
        this.props.dispatch(selectScores(values));
    }

    render() {
        if (!this.props.isLoaded) return null;
        return (
            <div>
                <label className="control-label">
                    Rating filter (optional):
                </label>
                <select
                    multiple
                    name="score_filter"
                    id="score_filter"
                    onChange={this.handleChange}
                    style={{ height: '120px' }}
                >
                    {_.map(this.props.choices, score => {
                        return (
                            <option key={score.id} value={score.id}>
                                {score.value}
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
        isLoaded: state.scores.isLoaded,
        choices: state.scores.items,
    };
}

export default connect(mapStateToProps)(ScoreSelect);
