import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import RobTasks from "../components/RobTasks";

@inject("robStore")
@observer
class RobRoot extends Component {
    render() {
        const store = this.props.robStore;
        return <RobTasks tasks={store.config.rob_tasks} showAssessment={store.showAssessment} />;
    }
}

RobRoot.propTypes = {
    robStore: PropTypes.object,
};

export default RobRoot;
