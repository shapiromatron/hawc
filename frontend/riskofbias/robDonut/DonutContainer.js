import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import Loading from "shared/components/Loading";

import Donut from "./Donut";
import RobDonutStore from "./store";

@observer
class DonutContainer extends Component {
    constructor(props) {
        super(props);
        this.ref = React.createRef();
        this.store = new RobDonutStore();
        this.donut = new Donut();
    }

    componentDidMount() {
        const {data} = this.props;
        this.store.fetchStudyDataAndSettings(data.studyId, data.assessmentId);
    }

    componentDidUpdate() {
        const {hasLoaded, hasFinalData, canShowScoreVisualization} = this.store;
        if (hasLoaded && hasFinalData && canShowScoreVisualization) {
            this.donut.render(this.store, this.ref.current);
        }
    }

    render() {
        const {hasLoaded, hasFinalData, canShowScoreVisualization} = this.store;
        if (!hasLoaded) {
            return <Loading />;
        }

        if (!hasFinalData) {
            return <p>No data available.</p>;
        }

        if (!canShowScoreVisualization) {
            return <p>Click button on right to view study evaluation details.</p>;
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
