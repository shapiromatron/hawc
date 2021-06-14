import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import Loading from "shared/components/Loading";

import Donut from "./Donut";
import StudyRobStore from "../stores/StudyRobStore";

@observer
class DonutContainer extends Component {
    constructor(props) {
        super(props);
        this.ref = React.createRef();
        this.store = new StudyRobStore();
        this.donut = new Donut();
    }

    componentDidMount() {
        const {data} = this.props;
        this.store.fetchStudyDataAndSettings(data.studyId, data.assessmentId);
    }

    componentDidUpdate() {
        if (this.store.isLoading) {
            return;
        }
        this.donut.render(this.store, this.ref.current);
    }

    render() {
        if (this.store.isLoading) {
            return <Loading />;
        }
        return <div ref={this.ref}></div>;
    }
}

DonutContainer.propTypes = {
    data: PropTypes.shape({
        studyId: PropTypes.number.isRequired,
        assessmentId: PropTypes.number.isRequired,
    }).isRequired,
};

export default DonutContainer;
