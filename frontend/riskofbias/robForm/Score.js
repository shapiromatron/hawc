import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

@observer
class Score extends Component {
    render() {
        return (
            <div>
                <h4>{this.props.score.id}</h4>
                <h4>{this.props.score.score}</h4>
            </div>
        );
    }
}

Score.propTypes = {
    score: PropTypes.shape({
        id: PropTypes.number.isRequired,
        score: PropTypes.number.isRequired,
    }).isRequired,
};

export default Score;
