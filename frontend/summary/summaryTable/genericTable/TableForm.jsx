import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import ColWidthTable from "./ColWidthTable";
import ConfigurationModal from "./ConfigurationModal";
import {EditCellModal} from "./EditCell";
import Table from "./Table";

@observer
class TableForm extends Component {
    render() {
        const {store} = this.props;
        return (
            <>
                <div className="bg-info p-2 clearfix">
                    <button className="btn btn-light mx-1" onClick={store.toggleShowColumnEdit}>
                        <i className="fa fa-arrows-h mr-1"></i>Column width
                    </button>
                    <div className="float-right">
                        <button
                            className="btn btn-light mr-5"
                            onClick={() => store.setConfigurationModal(true)}>
                            <i className="fa fa-cog mr-1"></i>Configuration
                        </button>
                        <button className="btn btn-light mx-1" onClick={store.addColumn}>
                            <i className="fa fa-plus mr-1"></i>Add column
                        </button>
                        <button className="btn btn-light mx-1" onClick={store.addRow}>
                            <i className="fa fa-plus mr-1"></i>Add row
                        </button>
                    </div>
                </div>
                {store.showColumnEdit ? <ColWidthTable store={store} /> : null}
                <h4>Editing table</h4>
                <p className="text-muted">
                    Click any cell to edit the text, or press the edit button on a cell to modify
                    the table structure (eg., merging rows and columns).
                </p>
                <Table store={store} />
                <EditCellModal store={store} />
                <ConfigurationModal store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
