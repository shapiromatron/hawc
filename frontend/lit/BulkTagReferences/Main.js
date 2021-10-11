import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import ReferenceMappingCard from "./ReferenceMappingCard";
import SpreadsheetCard from "./SpreadsheetCard";
import TagAssignmentCard from "./TagAssignmentCard";

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
                        <h3 className="card-title">#1. Load spreadsheet</h3>
                        <SpreadsheetCard />
                    </div>
                </div>
                <div className="card my-3">
                    <div className="card-body">
                        <h3 className="card-title">
                            #2. Match spreadsheet data to HAWC references
                        </h3>
                        <ReferenceMappingCard />
                    </div>
                </div>
                <div className="card my-3">
                    <div className="card-body">
                        <h3 className="card-title">#3. Apply reference tags</h3>
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
