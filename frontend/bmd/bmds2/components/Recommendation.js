import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";

import {bmdLabelText} from "bmd/common/constants";

import RecommendationNotes from "./RecommendationNotes";
import RecommendationTable from "./RecommendationTable";

class Recommendation extends React.Component {
    constructor(props) {
        super(props);
        this.state = this.updateState(props);
    }

    updateState(props) {
        let d;
        if (props.selectedModelId === null) {
            d = {
                bmr: props.models[0].bmr_id,
                model: null,
                notes: props.selectedModelNotes,
            };
        } else {
            let model = _.find(props.models, {id: props.selectedModelId});
            d = {
                bmr: model.bmr_id,
                model: model.id,
                notes: props.selectedModelNotes,
            };
        }
        return d;
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        this.setState(this.updateState(nextProps));
    }

    handleFieldChange(e) {
        let d = {},
            name = e.target.name,
            val = e.target.value;

        if (_.includes(["bmr", "model"], name)) {
            val = parseInt(val);
        }

        if (val === -1) {
            val = null;
        }

        d[name] = val;
        this.setState(d);
    }

    handleSaveSelected() {
        this.props.handleSaveSelected(this.state.model, this.state.notes);
    }

    renderForm() {
        let models = _.filter(this.props.models, {bmr_id: this.state.bmr}),
            selectedModel = this.state.model !== null ? this.state.model : -1;

        models.unshift({
            id: -1,
            name: "<no model selected>",
        });

        return (
            <>
                <legend>Select BMD model</legend>
                <form className="form">
                    <div className="col-md-4">
                        <label htmlFor="bmr">Selected BMR</label>
                        <div className="form-group">
                            <select
                                className="form-control"
                                value={this.state.bmr}
                                name="bmr"
                                onChange={this.handleFieldChange.bind(this)}>
                                {this.props.bmrs.map((d, i) => {
                                    return (
                                        <option key={i} value={i}>
                                            {bmdLabelText(d)}
                                        </option>
                                    );
                                })}
                            </select>
                        </div>

                        <label htmlFor="model">Selected model</label>

                        <div className="form-group">
                            <select
                                className="form-control"
                                value={selectedModel}
                                name="model"
                                onChange={this.handleFieldChange.bind(this)}>
                                {models.map(d => {
                                    return (
                                        <option key={d.id} value={d.id}>
                                            {d.name}
                                        </option>
                                    );
                                })}
                            </select>
                        </div>
                    </div>
                    <div className="col-md-8">
                        <label htmlFor="notes">Notes</label>
                        <div className="form-group">
                            <textarea
                                className="form-control"
                                value={this.state.notes}
                                onChange={this.handleFieldChange.bind(this)}
                                name="notes"
                                rows="5"
                                cols="40"
                            />
                            <p className="form-text text-muted">
                                Enter notes on why a model was selected as best fitting; if no model
                                is selected, add notes on why no model was selected.
                            </p>
                        </div>
                    </div>
                </form>
            </>
        );
    }

    renderWell() {
        return (
            <div className="well" key={1}>
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={this.handleSaveSelected.bind(this)}>
                    Save selected model
                </button>
            </div>
        );
    }

    renderUserNotes() {
        if (this.props.editMode) {
            return null;
        }
        return <RecommendationNotes notes={this.props.selectedModelNotes} />;
    }

    renderEditMode() {
        if (!this.props.editMode) {
            return null;
        }

        return [this.renderForm(), this.renderWell()];
    }

    render() {
        if (this.props.models.length === 0) {
            return null;
        }

        let modelSubset = _.filter(this.props.models, {
            bmr_id: this.state.bmr,
        });

        return (
            <div className="container-fluid">
                <RecommendationTable
                    models={modelSubset}
                    selectedModelId={this.props.selectedModelId}
                />
                {this.renderEditMode()}
                {this.renderUserNotes()}
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
