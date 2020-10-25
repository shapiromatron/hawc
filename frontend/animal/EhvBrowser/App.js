import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Table from "./Table";

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
        return (
            <>
                <div className="input-append">
                    <input
                        id="searchQuery"
                        className="col-md-6"
                        type="text"
                        value={this.state.query}
                        onChange={e => {
                            this.setState({query: e.target.value});
                            this.updateQuery();
                        }}
                    />
                </div>
                <Table />
            </>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
