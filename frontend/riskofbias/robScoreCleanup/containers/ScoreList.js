import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import h from "shared/utils/helpers";

import Loading from "shared/components/Loading";
import CheckboxScoreDisplay from "../components/CheckboxScoreDisplay";

@inject("store")
@observer
class ScoreList extends Component {
    render() {
        const {
            isFetchingStudyScores,
            studyScoresFetchTime,
            visibleStudyScores,
            selectedStudyScores,
        } = this.props.store;

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
                <div className="float-right">
                    <button
                        className="btn btn-secondary"
                        onClick={() => this.props.store.clearSelectedStudyScores()}>
                        Clear selected
                    </button>
                    <span>&nbsp;</span>
                    <button
                        className="btn btn-primary"
                        onClick={() => this.props.store.selectAllStudyScores()}>
                        Select all responses
                    </button>
                </div>
                <p className="lead">
                    {h.pluralize("response", visibleStudyScores.length)} met your criteria:
                </p>
                <br />
                {_.map(visibleStudyScores, studyScore => {
                    return (
                        <div key={studyScore.id}>
                            <CheckboxScoreDisplay
                                score={studyScore}
                                handleCheck={e =>
                                    this.props.store.changeSelectedStudyScores(
                                        studyScore.id,
                                        e.target.checked,
                                        studyScore.score,
                                        studyScore.notes
                                    )
                                }
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
