import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Alert from "shared/components/Alert";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class ReferenceMappingCard extends Component {
    render() {
        const {store} = this.props,
            {referenceMap, referenceIdColumn} = store,
            nMatchedRows = store.matchedDatasetRows.length,
            nUnmatchedRows = store.unmatchedDatasetRows.length;

        if (!store.hasValidXlsx) {
            return (
                <p className="text-muted">Please complete the previous step before continuing</p>
            );
        }

        return (
            <div className="row">
                <div className="col-md-6">
                    <SelectInput
                        choices={store.datasetColumnChoices}
                        handleSelect={store.setReferenceIdColumn}
                        value={store.referenceIdColumn}
                        label="Reference ID column"
                        helpText="Select the column in the spreadsheet which can be used to match references loaded in HAWC"
                    />
                </div>
                <div className="col-md-6">
                    <SelectInput
                        choices={store.referenceColumnTypeChoices}
                        handleSelect={store.setReferenceColumnType}
                        value={store.referenceColumnType}
                        label="Reference ID column type"
                        helpText="Select what type of reference unique identifier is present in this column. HAWC references must also have the same reference identifier properly assigned in order to match."
                    />
                </div>
                <div
                    className={nUnmatchedRows > 0 ? "col-md-6 resize-y" : "col-md-12 resize-y"}
                    style={{height: 400}}>
                    <p className="float-right text-muted mb-2">
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
                {nUnmatchedRows > 0 ? (
                    <div className="col-md-6 resize-y" style={{height: 400}}>
                        <p className="float-right text-muted mb-2">
                            {nUnmatchedRows} row(s) where a matching HAWC reference cannot be
                            determined.
                        </p>
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
                    </div>
                ) : null}
                <div className="col-md-12 mt-3">
                    {nMatchedRows == 0 && nUnmatchedRows == 0 ? null : nMatchedRows > 0 &&
                      nUnmatchedRows > 0 ? (
                        <Alert
                            className="alert-warning"
                            icon="fa-question-circle"
                            message="Some, but not all, rows were matched to references in HAWC. This may be an issue if you'd like to apply tags to rows which we cannot map to references. If this is the case, you may want to revise the spreadsheet, or ensure that existing HAWC references are appropriately associated with the identifier you are trying to use."
                        />
                    ) : nMatchedRows > 0 ? (
                        <Alert
                            className="alert-success"
                            icon="fa-check-square"
                            message="All rows in the spreadsheet were successfully matched to references in HAWC - ok to continue!"
                        />
                    ) : (
                        <Alert message="No rows were matched to any HAWC references. Please revise the reference mapping selections, or ensure HAWC references are appropriately associated with the identifier you are trying to use." />
                    )}
                </div>
            </div>
        );
    }
}
ReferenceMappingCard.propTypes = {
    store: PropTypes.object,
};

export default ReferenceMappingCard;
