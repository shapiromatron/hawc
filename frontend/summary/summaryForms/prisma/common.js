import PropTypes from "prop-types";
import React, {Component} from "react";

class MissingData extends Component {
    render() {
        return (
            <div className="alert alert-warning" role="alert">
                Data is missing; update settings on the Data tab and press &quot;Fetch data&quot;.
            </div>
        );
    }
}

class RefreshRequired extends Component {
    render() {
        return (
            <div className="alert alert-warning" role="alert">
                A data refresh is required; press &quot;Fetch data&quot; on settings page.
            </div>
        );
    }
}

export {MissingData, RefreshRequired};
