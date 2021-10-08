import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Alert from "shared/components/Alert";
import FileInput from "shared/components/FileInput";
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import Loading from "shared/components/Loading";
import FormActions from "shared/components/FormActions";

@inject("store")
@observer
class SpreadsheetCard extends Component {
    render() {
        const {store} = this.props,
            {handleFileInput, hasAssessmentData, hasValidXlsx} = store;
        if (!hasAssessmentData) {
            return null;
        }
        return (
            <>
                <FileInput
                    onChange={handleFileInput}
                    helpText="Select an Excel file (.xlsx) to load and process. The first worksheet will be processed. The spreadsheet should contain data in a rectangular data format."
                />
                {hasValidXlsx ? (
                    <div className="row">
                        <ul>
                            <li>{store.dataset.length} rows</li>
                            <li>{store.datasetColumns.length} columns</li>
                            <li>Columns: {store.datasetColumns.join(", ")}</li>
                        </ul>
                    </div>
                ) : null}
            </>
        );
    }
}
SpreadsheetCard.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class ReferenceMappingCard extends Component {
    render() {
        const {store} = this.props,
            {referenceMap, referenceIdColumn} = store,
            nMatchedRows = store.matchedDatasetRows.length,
            nUnmatchedRows = store.unmatchedDatasetRows.length;
        return store.hasValidXlsx ? (
            <div className="row">
                <div className="col-md-6">
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        handleSelect={store.setReferenceIdColumn}
                        value={store.referenceIdColumn}
                        label="Reference ID column"
                        helpText="Select the column in the spreadsheet which can be used to match to a HAWC reference"
                    />
                </div>
                <div className="col-md-6">
                    <SelectInput
                        choices={store.referenceColumnTypeChoices}
                        handleSelect={store.setReferenceColumnType}
                        value={store.referenceColumnType}
                        label="Reference ID column type"
                        helpText="Select what type of reference ID is present in this column. HAWC references must also have the same reference in order to match."
                    />
                </div>
                <div className="col-md-6 resize-y" style={{height: 400}}>
                    <p className="pull-right text-muted mb-2">
                        {nMatchedRows} row(s) which match HAWC reference.
                    </p>
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
                                {store.matchedDatasetRows.map(row => {
                                    const id = referenceMap.get(row[referenceIdColumn]);
                                    return (
                                        <tr key={row.__index__}>
                                            <td>{row.__index__}</td>
                                            <td>{row[referenceIdColumn]}</td>
                                            <td>
                                                <a
                                                    href={`/lit/reference/${id}/`}
                                                    target="_blank"
                                                    rel="noreferrer">
                                                    {id}
                                                </a>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    ) : null}
                </div>
                <div className="col-md-6 resize-y" style={{height: 400}}>
                    <p className="pull-right text-muted mb-2">
                        {nUnmatchedRows} row(s) where a matching HAWC reference cannot be
                        determined.
                    </p>
                    {nUnmatchedRows > 0 ? (
                        <table className="table table-condensed table-sm">
                            <thead>
                                <tr>
                                    <th>Row #</th>
                                    <th>{referenceIdColumn}</th>
                                    <th>HAWC Reference</th>
                                </tr>
                            </thead>
                            <tbody>
                                {store.unmatchedDatasetRows.map(row => {
                                    return (
                                        <tr key={row.__index__}>
                                            <td>{row.__index__}</td>
                                            <td>{row[referenceIdColumn]}</td>
                                            <td>
                                                <i>&lt;not found&gt;</i>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    ) : null}
                </div>
                <div className="col-md-12 mt-3">
                    {nMatchedRows == 0 && nUnmatchedRows == 0 ? null : nMatchedRows > 0 &&
                      nUnmatchedRows > 0 ? (
                        <Alert
                            className="alert-warning"
                            icon="fa-question-circle"
                            message="Some rows matched references in HAWC. This may be an issue if you'd like to bulk apply tags to rows which we were unable to match. If this is the case, you may want to revise the spreadsheet and/or existing HAWC references for more matches."
                        />
                    ) : nMatchedRows > 0 ? (
                        <Alert
                            className="alert-success"
                            icon="fa-check-square"
                            message="All rows successfully matched. Ok to continue!"
                        />
                    ) : (
                        <Alert message="No rows matched. Please select a different row." />
                    )}
                </div>
            </div>
        ) : (
            <p className="text-muted">Please complete the previous step before continuing</p>
        );
    }
}
ReferenceMappingCard.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class TagAssignmentCard extends Component {
    render() {
        const {store} = this.props,
            {referenceIdColumn} = store,
            nMatchedRows = store.matchedRowsWithValue.length,
            nUnmatchedRows = store.unmatchedRowsWithValue.length;
        return store.hasMatchingReferences ? (
            <div className="row">
                <div className="col-md-6">
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        handleSelect={store.setDatasetTagColumn}
                        value={store.datasetTagColumn}
                        label="Spreadsheet column"
                        helpText="Column in the spreadsheet that can be used to apply tags."
                    />
                    <SelectInput
                        choices={store.datasetTagValueChoices}
                        handleSelect={store.setDatasetTagValue}
                        value={store.datasetTagValue}
                        label="Spreadsheet column value"
                        helpText="The value in the selected column"
                    />
                </div>
                <div className="col-md-6">
                    <SelectInput
                        choices={store.tagChoices}
                        handleSelect={store.setTag}
                        value={store.tag}
                        label="Select HAWC tag"
                        helpText="Select HAWC tag to apply or remove from matching references"
                    />
                    <RadioInput
                        label="Create or delete tags:"
                        name="tags"
                        onChange={store.setTagVerb}
                        value={store.tagVerb}
                        choices={store.tagVerbChoices}
                    />
                </div>
                {store.hasDatasetTagValue ? (
                    <>
                        <div className="col-md-6">
                            <p className="pull-right text-muted mb-2">
                                {nMatchedRows} rows where&nbsp;
                                {store.datasetTagColumn} equals &quot;
                                {store.datasetTagValue}&quot; and a HAWC reference exists.
                            </p>
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
                        <div className="col-md-6">
                            <p className="pull-right text-muted mb-2">
                                {nUnmatchedRows} rows where&nbsp;
                                {store.datasetTagColumn} equals &quot;
                                {store.datasetTagValue}&quot; and a matching HAWC reference cannot
                                be determined.
                            </p>
                            {nUnmatchedRows > 0 ? (
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
                            ) : null}
                        </div>
                        <div className="col-md-12 mt-3">
                            {nMatchedRows == 0 && nUnmatchedRows == 0 ? null : nMatchedRows > 0 &&
                              nUnmatchedRows > 0 ? (
                                <Alert
                                    className="alert-warning"
                                    icon="fa-question-circle"
                                    message="Some rows with this value are matched, but not all. Changes made in HAWC using this value will be inconsistent wih the spreadsheet."
                                />
                            ) : nMatchedRows > 0 ? (
                                <Alert
                                    className="alert-success"
                                    icon="fa-check-square"
                                    message="All references matched, and tag can successfully be applied!"
                                />
                            ) : (
                                <Alert message="No rows with this value are matched in HAWC." />
                            )}
                        </div>
                        {store.canBeSubmitted ? (
                            <div className="col-md-12">
                                <FormActions
                                    handleSubmit={store.submitForm}
                                    submitText="Apply"
                                    cancel={store.resetForm}
                                    cancelText="Reset"
                                />
                            </div>
                        ) : null}
                    </>
                ) : null}
            </div>
        ) : (
            <p className="text-muted">Please complete the previous step before continuing</p>
        );
    }
}
TagAssignmentCard.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class BulkTagReferencesMain extends Component {
    componentDidMount() {
        this.props.store.fetchReferences();
        this.props.store.fetchTags();
    }

    render() {
        const {store} = this.props;

        return (
            <>
                <h2>Bulk tag references</h2>
                <div className="text-muted">
                    <p>
                        Bulk tag references using data from an Excel spreadsheet. Data from the
                        spreadsheet is expected to come from an external system where tags have
                        already been applied in that system, and they will be migrated to this
                        system. Before tagging, make sure the following are complete:
                    </p>
                    <ol>
                        <li>
                            References have been uploaded into HAWC with appropriate database IDs
                        </li>
                        <li>The tag structure in HAWC is complete</li>
                    </ol>
                </div>
                {store.hasAssessmentData ? null : <Loading />}
                <div className="card my-3">
                    <div className="card-body">
                        <h3 className="card-title">#1 Load spreadsheet</h3>
                        <SpreadsheetCard />
                    </div>
                </div>
                <div className="card my-3">
                    <div className="card-body">
                        <h3 className="card-title">#2 Match spreadsheet data to HAWC references</h3>
                        <ReferenceMappingCard />
                    </div>
                </div>
                <div className="card my-3">
                    <div className="card-body">
                        <h3 className="card-title">#3 Apply reference tags</h3>
                        <TagAssignmentCard />
                    </div>
                </div>
            </>
        );
    }
}
BulkTagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default BulkTagReferencesMain;
