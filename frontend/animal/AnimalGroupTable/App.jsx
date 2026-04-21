import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import AnimalGroupTable from "./AnimalGroupTable";
import NoDoseResponseList from "./NoDoseResponseList";

@inject("store")
@observer
class App extends Component {
    render() {
        const {store} = this.props;
        return (
            <>
                <h3>Available endpoints</h3>
                {!store.hasEndpoints ? (
                    <p>No endpoints are available.</p>
                ) : (
                    <>
                        <AnimalGroupTable />
                        <NoDoseResponseList />
                    </>
                )}
            </>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
