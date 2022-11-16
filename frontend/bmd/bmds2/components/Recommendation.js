import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

import RecommendationNotes from "./RecommendationNotes";
import RecommendationTable from "./RecommendationTable";

class Recommendation extends React.Component {
    constructor(props) {
        super(props);
        this.state = this.updateState(props);
    }

    updateState(props) {
        let d = {
            bmr: props.models[0].bmr_id,
            model: null,
            notes: props.selectedModelNotes,
        };
        if (props.selectedModelId) {
            // get select model. this may be null if the selected model is from another bmd session.
            let model = _.find(props.models, {id: props.selectedModelId});
            if (model) {
                d = {
                    bmr: model.bmr_id,
                    model: model.id,
                    notes: props.selectedModelNotes,
                };
            }
        }
        return d;
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        this.setState(this.updateState(nextProps));
    }

    render() {
        const {bmr} = this.state,
            {models, selectedModelId} = this.props,
            modelSubset = _.filter(models, {bmr_id: bmr});

        if (models.length === 0) {
            return null;
        }
        return (
            <div className="container-fluid">
                <RecommendationTable models={modelSubset} selectedModelId={selectedModelId} />
                <RecommendationNotes notes={this.props.selectedModelNotes} />
            </div>
        );
    }
}

Recommendation.propTypes = {
    selectedModelId: PropTypes.number,
    selectedModelNotes: PropTypes.string.isRequired,
    models: PropTypes.array.isRequired,
    bmrs: PropTypes.array.isRequired,
};

export default Recommendation;
