import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

@inject("store")
@observer
class Table extends Component {
    render() {
        const {filteredDataset} = this.props.store;
        return (
            <table className="table table-condensed table-striped">
                <thead>
                    <tr>
                        <th>System</th>
                        <th>Organ</th>
                        <th>Effect</th>
                        <th>Effect subtype</th>
                        <th>Name</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredDataset.map(d => (
                        <tr key={d._key}>
                            <td>{d.system}</td>
                            <td>{d.organ}</td>
                            <td>{d.effect}</td>
                            <td>{d.effect_subtype}</td>
                            <td>{d.endpoint_name}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    }
}
Table.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class App extends Component {
    componentDidMount() {
        this.props.store.filterDataset();
    }
    render() {
        const {filterDataset, query, updateQuery, isFiltering} = this.props.store;
        return (
            <>
                <div className="input-append">
                    <input
                        id="searchQuery"
                        className="span6"
                        type="text"
                        value={query}
                        onChange={e => updateQuery(e.target.value)}
                    />
                    <button className="btn btn-info" type="button" onClick={() => filterDataset()}>
                        Search
                    </button>
                </div>
                {isFiltering ? <Loading /> : <Table />}
            </>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
