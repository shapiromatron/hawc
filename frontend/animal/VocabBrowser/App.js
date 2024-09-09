import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import EhvTable from "./EhvBrowser/Table";
import ToxRefDBTable from "./ToxRefDBBrowser/Table";

@inject("store")
@observer
class App extends Component {
    constructor(props) {
        // this pattern effectively "debounces" the computed value from the datastore
        // https://stackoverflow.com/a/50999795/906385
        super(props);
        this.state = {
            query: "",
        };
        this.updateQuery = _.debounce(() => props.store.updateQuery(this.state.query), 100);
    }

    render() {
        const tables = {ehv: EhvTable, toxrefdb: ToxRefDBTable},
            Table = tables[this.props.store.config.vocab];

        return (
            <>
                <div className="input-group">
                    <input
                        id="searchQuery"
                        className="form-control"
                        type="text"
                        value={this.state.query}
                        onChange={e => {
                            this.setState({query: e.target.value});
                            this.updateQuery();
                        }}
                    />
                </div>
                {_.isUndefined(Table) ? <p>ERROR - unknown vocabulary</p> : <Table />}
            </>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
