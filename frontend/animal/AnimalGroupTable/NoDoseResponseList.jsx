import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

@inject("store")
@observer
class NoDoseResponseList extends Component {
    render() {
        const {endpointsNoDr} = this.props.store;
        if (endpointsNoDr.length === 0) {
            return null;
        }
        return (
            <>
                <h3>Additional endpoints</h3>
                <p>Endpoints which have no dose-response data extracted.</p>
                <ul>
                    {endpointsNoDr.map(endpoint => {
                        return (
                            <li key={endpoint.data.id}>
                                <a href={endpoint.data.url}>{endpoint.data.name}</a>
                            </li>
                        );
                    })}
                </ul>
            </>
        );
    }
}
NoDoseResponseList.propTypes = {
    store: PropTypes.object,
};

export default NoDoseResponseList;
