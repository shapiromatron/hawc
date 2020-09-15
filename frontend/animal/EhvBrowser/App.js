import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class App extends Component {
    render() {
        const {filteredDataset, query, updateQuery} = this.props.store;
        return (
            <div>
                <input
                    type="string"
                    value={query}
                    onChange={_.throttle(e => updateQuery(e.target.value), 500)}
                />
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
                        {filteredDataset.map((d, i) => (
                            <tr key={i}>
                                <td>{d.system}</td>
                                <td>{d.organ}</td>
                                <td>{d.effect}</td>
                                <td>{d.effect_subtype}</td>
                                <td>{d.endpoint_name}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
