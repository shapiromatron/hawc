import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Alert from "shared/components/Alert";
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import Loading from "shared/components/Loading";
import FormActions from "shared/components/FormActions";

@inject("store")
@observer
class TagAssignmentCard extends Component {
    render() {
        const {store} = this.props;

        if (!store.hasMatchingReferences) {
            return (
                <p className="text-muted">Please complete the previous step before continuing</p>
            );
        }

        return (
            <div className="row">
                <div className="col-md-6">
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        handleSelect={store.setDatasetTagColumn}
                        value={store.datasetTagColumn}
                        label="Spreadsheet column"
                        helpText="Column in the spreadsheet which can be used to apply tags"
                    />
                    <SelectInput
                        choices={store.datasetTagValueChoices}
                        handleSelect={store.setDatasetTagValue}
                        value={store.datasetTagValue}
                        label="Spreadsheet column value"
                        helpText="The value in the selected column which should be used to assign tags"
                    />
                </div>
                <div className="col-md-6">
                    <SelectInput
                        choices={store.tagChoices}
                        handleSelect={store.setTag}
                        value={store.tag}
                        label="Select HAWC tag"
                        helpText="The tag to apply selected to selected references"
                    />
                    <RadioInput
                        label="Apply or remove tags:"
                        name="tags"
                        onChange={store.setTagVerb}
                        value={store.tagVerb}
                        choices={store.tagVerbChoices}
                    />
                </div>
                {this.renderTagAssignment()}
                {this.renderSubmission()}
            </div>
        );
    }

    renderTagAssignment() {
        const {store} = this.props;

        if (!store.hasDatasetTagValue) {
            return null;
        }

        const {referenceIdColumn} = store,
            nMatchedRows = store.matchedRowsWithValue.length,
            nUnmatchedRows = store.unmatchedRowsWithValue.length,
            matchedMsg = `${nMatchedRows} rows where ${store.datasetTagColumn} equals "${store.datasetTagValue}" and a HAWC reference matched.`,
            unmatchedMessage = `${nUnmatchedRows} rows where ${store.datasetTagColumn} equals "${store.datasetTagValue}" and a HAWC reference cannot be determined.`;

        return (
            <>
                <div
                    className={nUnmatchedRows > 0 ? "col-md-6 resize-y" : "col-md-12 resize-y"}
                    style={{height: 400}}>
                    <p className="float-right text-muted mb-2">{matchedMsg}</p>
                    {nMatchedRows > 0 ? (
                        <table className="table table-condensed table-sm">
                            <thead>
                                <tr>
                                    <th>Row #</th>
                                    <th>{referenceIdColumn}</th>
                                    <th>HAWC Reference</th>
                                </tr>
                            </thead>
                            <tbody>
                                {store.matchedRowsWithValue.map(row => {
                                    return (
                                        <tr key={row.__index__}>
                                            <td>{row.__index__}</td>
                                            <td>{row.referenceValue}</td>
                                            <td>
                                                <a
                                                    href={`/lit/reference/${row.reference_id}/`}
                                                    target="_blank"
                                                    rel="noreferrer">
                                                    {row.reference_id}
                                                </a>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    ) : null}
                </div>
                {nUnmatchedRows > 0 ? (
                    <div className="col-md-6 resize-y" style={{height: 400}}>
                        <p className="float-right text-muted mb-2">{unmatchedMessage}</p>
                        <table className="table table-condensed table-sm">
                            <thead>
                                <tr>
                                    <th>Row #</th>
                                    <th>{referenceIdColumn}</th>
                                    <th>HAWC Reference</th>
                                </tr>
                            </thead>
                            <tbody>
                                {store.unmatchedRowsWithValue.map(row => {
                                    return (
                                        <tr key={row.__index__}>
                                            <td>{row.__index__}</td>
                                            <td>{row.referenceValue}</td>
                                            <td>
                                                <i>&lt;not found&gt;</i>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                ) : null}
                <div className="col-md-12 mt-3">
                    {nMatchedRows == 0 && nUnmatchedRows == 0 ? null : nMatchedRows > 0 &&
                      nUnmatchedRows > 0 ? (
                        <Alert
                            className="alert-warning"
                            icon="fa-question-circle"
                            message="Some rows with this value are matched to a HAWC reference, but not all. Changes made in HAWC using this value will be inconsistent with the spreadsheet."
                        />
                    ) : nMatchedRows > 0 ? (
                        <Alert
                            className="alert-success"
                            icon="fa-check-square"
                            message="All rows matched to a HAWC reference; tag can successfully be applied!"
                        />
                    ) : (
                        <Alert message="No rows with this value are matched in HAWC." />
                    )}
                </div>
            </>
        );
    }

    renderSubmission() {
        const {store} = this.props;

        if (!store.canBeSubmitted) {
            return null;
        }

        const nMatchedRows = store.matchedRowsWithValue.length,
            actionVerb = store.tagVerb === "append" ? "added to" : "removed from",
            matchTense = store.matchedRowsWithValue.length > 1 ? "s" : "",
            submitSuccessMessage = `Tag was ${actionVerb} ${nMatchedRows} reference${matchTense}.`,
            submitFailureMessage = `An error occurred - the tag was not ${actionVerb} ${nMatchedRows} reference${matchTense}.`;

        return (
            <div className="col-md-12">
                <FormActions
                    handleSubmit={store.submitForm}
                    submitText="Apply"
                    cancel={store.resetForm}
                    cancelText="Reset"
                />
                {store.isSubmitting ? <Loading /> : null}
                {store.submissionSuccessful === null ? null : store.submissionSuccessful ? (
                    <Alert
                        className="alert-success"
                        icon="fa-check-square"
                        message={submitSuccessMessage}
                    />
                ) : (
                    <Alert message={submitFailureMessage} />
                )}
            </div>
        );
    }
}
TagAssignmentCard.propTypes = {
    store: PropTypes.object,
};

export default TagAssignmentCard;
