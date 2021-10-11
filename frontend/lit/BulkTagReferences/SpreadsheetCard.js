import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import FileInput from "shared/components/FileInput";

@inject("store")
@observer
class SpreadsheetCard extends Component {
    renderMetadata() {
        const {store} = this.props,
            {hasValidXlsx} = store;
        if (!hasValidXlsx) {
            return null;
        }
        return (
            <div className="row">
                <ul>
                    <li>{store.dataset.length} rows</li>
                    <li>{store.datasetColumns.length} columns</li>
                    <li>Columns: {store.datasetColumns.join(", ")}</li>
                </ul>
            </div>
        );
    }
    render() {
        const {store} = this.props,
            {handleFileInput, hasAssessmentData} = store;
        if (!hasAssessmentData) {
            return null;
        }
        return (
            <>
                <FileInput
                    onChange={handleFileInput}
                    helpText="Select an Excel file (.xlsx) to load and process. The first worksheet will be processed. The spreadsheet should contain data in a rectangular data format."
                />
                {this.renderMetadata()}
            </>
        );
    }
}
SpreadsheetCard.propTypes = {
    store: PropTypes.object,
};

export default SpreadsheetCard;
