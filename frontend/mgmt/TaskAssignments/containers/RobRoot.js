import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import RobTasks from "../components/RobTasks";

@inject("robStore")
@observer
class RobRoot extends Component {
    render() {
        const store = this.props.robStore;
        return (
            <RobTasks
                tasks={store.config.rob_tasks}
                studies={store.config.rob_studies}
                showAssessment={store.showAssessment}
            />
        );
    }
}

RobRoot.propTypes = {
    robStore: PropTypes.object,
};

export default RobRoot;
