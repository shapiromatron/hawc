import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import DjangoForm from "./DjangoForm";

@inject("store")
@observer
class Root extends Component {
    render() {
        return <DjangoForm />;
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
