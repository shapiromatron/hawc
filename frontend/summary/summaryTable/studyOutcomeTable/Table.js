import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";

@observer
class Table extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
    }
    render() {
        const {store} = this.props;
        if (!store.hasData) {
            return <Loading />;
        }
        return (
            <table className="summaryTable table table-bordered table-sm">
                <thead>
                    <tr>
                        <th>TODO.</th>
                    </tr>
                </thead>
            </table>
        );
    }
}

Table.defaultProps = {
    forceReadOnly: false,
};
Table.propTypes = {
    store: PropTypes.object.isRequired,
    forceReadOnly: PropTypes.bool,
};

export default Table;
