import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import HelpTextPopup from "shared/components/HelpTextPopup";

import {testFootnotes} from "../constants";
import {fractionalFormatter} from "../formatters";
import Table from "./Table";

@inject("store")
@observer
class DatasetTable extends React.Component {
    render() {
        const {store, withResults} = this.props,
            datasetTableProps = _.cloneDeep(store.datasetTableProps);

        if (withResults && store.isContinuous) {
            const p_values = store.outputs.models[0].results.tests.p_values;
            datasetTableProps.footer = (
                <div className="text-left">
                    <>
                        <p className="text-muted my-0">
                            Test 1
                            <HelpTextPopup title={"Test 1"} content={testFootnotes[1]} />
                            &nbsp;Dose Response: {fractionalFormatter(p_values[0])}
                        </p>
                        <p className="text-muted my-0">
                            Test 2
                            <HelpTextPopup title={"Test 2"} content={testFootnotes[2]} />
                            &nbsp;Homogeneity of Variance: {fractionalFormatter(p_values[1])}
                        </p>
                        <p className="text-muted my-0">
                            Test 3
                            <HelpTextPopup title={"Test 3"} content={testFootnotes[3]} />
                            &nbsp;Variance Model Selection: {fractionalFormatter(p_values[2])}
                        </p>
                    </>
                </div>
            );
        }

        return <Table {...datasetTableProps} />;
    }
}
DatasetTable.propTypes = {
    store: PropTypes.object,
    withResults: PropTypes.bool,
};
DatasetTable.defaultProps = {
    withResults: false,
};

export default DatasetTable;
