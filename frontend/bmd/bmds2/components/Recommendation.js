import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";

import {bmdLabelText} from "bmd/common/constants";
import SelectInput from "shared/components/SelectInput";
import TextAreaInput from "shared/components/TextAreaInput";

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

    renderForm() {
        const {bmrs, models, handleSaveSelected} = this.props,
            {bmr, model, notes} = this.state,
            selectedModel = model !== null ? model : -1,
            handleSelectChange = (name, value) => {
                const d = {};
                d[name] = parseInt(value);
                if (d[name] === -1) {
                    d[name] = null;
                }
                this.setState(d);
            },
            bmrChoices = bmrs.map((d, idx) => {
                return {id: idx, label: bmdLabelText(d)};
            }),
            modelChoices = models
                .filter(d => d.bmr_id == bmr)
                .map(d => {
                    return {id: d.id, label: d.name};
                });

        modelChoices.unshift({id: -1, label: "<no model selected>"});

        return (
            <div className="row">
                <div className="col-md-12">
                    <legend>Select BMD model</legend>
                </div>
                <div className="col-md-4">
                    <SelectInput
                        label="Selected BMR"
                        choices={bmrChoices}
                        value={bmr}
                        handleSelect={value => handleSelectChange("bmr", value)}
                    />
                    <SelectInput
                        label="Selected model"
                        choices={modelChoices}
                        value={selectedModel}
                        handleSelect={value => handleSelectChange("model", value)}
                    />
                </div>
                <div className="col-md-8">
                    <TextAreaInput
                        name="notes"
                        label="Notes"
                        value={notes}
                        onChange={e => this.setState({notes: e.target.value})}
                        helpText={`Enter notes on why a model was selected as best fitting;
                            if no model is selected, add notes on why no model was selected.`}
                    />
                </div>
                <div className="well col-md-12">
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => handleSaveSelected(model, notes)}>
                        Save selected model
                    </button>
                </div>
            </div>
        );
    }

    render() {
        const {bmr} = this.state,
            {editMode, models, selectedModelId} = this.props,
            modelSubset = _.filter(models, {bmr_id: bmr});

        if (models.length === 0) {
            return null;
        }
        return (
            <div className="container-fluid">
                <RecommendationTable models={modelSubset} selectedModelId={selectedModelId} />
                {editMode ? (
                    this.renderForm()
                ) : (
                    <RecommendationNotes notes={this.props.selectedModelNotes} />
                )}
            </div>
        );
    }
}

Recommendation.propTypes = {
    editMode: PropTypes.bool.isRequired,
    selectedModelId: PropTypes.number,
    selectedModelNotes: PropTypes.string.isRequired,
    handleSaveSelected: PropTypes.func.isRequired,
    models: PropTypes.array.isRequired,
    bmrs: PropTypes.array.isRequired,
};

export default Recommendation;
