import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import Score from "./Score";

@observer
class Metric extends Component {
    render() {
        const anyScore = this.props.scores[0],
            name = anyScore.metric.name,
            hideDescription = anyScore.metric.hide_description,
            description = anyScore.metric.description;

        return (
            <div>
                <h4>{name}</h4>
                {hideDescription ? null : <div dangerouslySetInnerHTML={{__html: description}} />}
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
