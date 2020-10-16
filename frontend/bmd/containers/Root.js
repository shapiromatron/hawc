import React from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Tabs from "bmd/containers/Tabs";
import Modals from "bmd/containers/Modals";

@inject("store")
@observer
class Root extends React.Component {
    render() {
        return (
            <>
                <Tabs />
                <Modals />
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
