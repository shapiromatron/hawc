import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

@inject("store")
@observer
class TagReferencesMain extends Component {
    render() {
        const {store} = this.props;
        return (
            <div className="row-fluid">
                <h1>Let's tag some references</h1>
                <Loading />
            </div>
        );
    }
}

TagReferencesMain.propTypes = {
    store: PropTypes.object,
};

export default TagReferencesMain;
