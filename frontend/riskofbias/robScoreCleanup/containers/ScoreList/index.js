import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import CheckboxScoreDisplay from "../../components/CheckboxScoreDisplay";

@inject("store")
@observer
class ScoreList extends Component {
    render() {
        const {
                isFetchingStudyScores,
                studyScoresFetchTime,
                visibleStudyScores,
                selectedStudyScores,
            } = this.props.store,
            handleCheck = e => {
                this.props.store.changeSelectedStudyScores(parseInt(e.target.id), e.target.checked);
            };

        if (isFetchingStudyScores) {
            return <Loading />;
        }

        if (studyScoresFetchTime === null) {
            return null;
        }

        if (visibleStudyScores.length === 0) {
            return <p className="lead">No items meet your criteria.</p>;
        }

        return (
            <div>
                <h4>RoB responses which meet criteria specified above:</h4>
                {_.map(visibleStudyScores, studyScore => {
                    return (
                        <div key={studyScore.id}>
                            <CheckboxScoreDisplay
                                score={studyScore}
                                handleCheck={handleCheck}
                                checked={selectedStudyScores.has(studyScore.id)}
                            />
                            <hr />
                        </div>
                    );
                })}
            </div>
        );
    }
}
ScoreList.propTypes = {
    store: PropTypes.object,
};

export default ScoreList;
