import React from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import h from "shared/utils/helpers";

import {ScoreInput, ScoreNotesInput} from "../../robStudyForm/ScoreForm";

@inject("store")
@observer
class MetricForm extends React.Component {
    render() {
        const {store} = this.props,
            numItems = this.props.store.selectedStudyScores.size;

        if (store.selectedStudyScores.size === 0) {
            return null;
        }
        return (
            <div className="row bulkEditForm">
                <div className="col-md-5">
                    <ScoreInput
                        scoreId={-1}
                        choices={store.scoreOptions.map(d => d.id)}
                        value={store.formScore}
                        handleChange={value => store.setFormScore(parseInt(value))}
                    />
                    <button
                        className="btn btn-primary"
                        type="button"
                        onClick={store.bulkUpdateSelectedStudies}>
                        Bulk modify {h.pluralize("item", numItems)}.
                    </button>
                    <p className="form-text text-muted">
                        Submitting this request will change the selected score and notes for the
                        selected items.
                    </p>
                </div>
                <div className="col-md-7">
                    <ScoreNotesInput
                        scoreId={-1}
                        value={store.formNotes}
                        handleChange={value => store.setFormNotes(value)}
                    />
                </div>
            </div>
        );
    }
}
MetricForm.propTypes = {
    store: PropTypes.object,
};

export default MetricForm;
