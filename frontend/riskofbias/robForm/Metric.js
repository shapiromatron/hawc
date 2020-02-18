import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import Score from "./Score";

@observer
class Metric extends Component {
    render() {
        let metricName = this.props.scores[0].metric.name;
        return (
            <div>
                <h4>{metricName}</h4>
                {this.props.scores.map(score => {
                    return <Score key={score.id} score={score} />;
                })}
            </div>
        );
    }
}

Metric.propTypes = {
    metricId: PropTypes.number.isRequired,
    scores: PropTypes.array.isRequired,
};

export default Metric;
