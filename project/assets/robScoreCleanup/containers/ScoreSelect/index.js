import React from 'react';
import { connect } from 'react-redux';

import { selectScores } from 'robScoreCleanup/actions/Scores';


export class ScoreSelect extends React.Component {

    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);   
    }

    handleChange({ target: {options} }) {
        let values = [...options].filter((o) => o.selected).map((o) => o.value);
        this.props.dispatch(selectScores(values));
    }

    render() {
        return (
            <div>
                <select multiple name="score_filter" id="score_filter" onChange={this.handleChange}>
                {_.map(this.props.choices, (score) => {
                    return <option key={score.id} value={score.id}>{score.value}</option>;
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
