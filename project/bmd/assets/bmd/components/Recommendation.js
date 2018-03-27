import _ from 'lodash';
import React from 'react';
import PropTypes from 'prop-types';

import { asLabel } from 'bmd/models/bmr';

import RecommendationNotes from './RecommendationNotes';
import RecommendationTable from './RecommendationTable';

class Recommendation extends React.Component {
    updateState(props) {
        let d;
        if (props.selectedModelId === null) {
            d = {
                bmr: props.models[0].bmr_id,
                model: -1,
                notes: props.selectedModelNotes,
            };
        } else {
            let model = _.find(props.models, { id: props.selectedModelId });
            d = {
                bmr: model.bmr_id,
                model: model.id,
                notes: props.selectedModelNotes,
            };
        }
        this.setState(d);
    }

    componentWillMount() {
        this.updateState(this.props);
    }

    componentWillReceiveProps(nextProps) {
        this.updateState(nextProps);
    }

    handleFieldChange(e) {
        let d = {},
            name = e.target.name,
            val = e.target.value;

        if (_.includes(['bmr', 'model'], name)) {
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
        let models = _.filter(this.props.models, { bmr_id: this.state.bmr }),
            selectedModel = this.state.model !== null ? this.state.model : -1;

        models.unshift({
            id: -1,
            name: '<no model selected>',
        });

        return (
            <div className="row-fluid" key={0}>
                <legend>Select BMD model</legend>
                <form className="form">
                    <div className="span4">
                        <label htmlFor="bmr" className="control-label">
                            Selected BMR
                        </label>
                        <div className="controls">
                            <select
                                className="span12"
                                value={this.state.bmr}
                                name="bmr"
                                onChange={this.handleFieldChange.bind(this)}
                            >
                                {this.props.bmrs.map((d, i) => {
                                    return (
                                        <option key={i} value={i}>
                                            {asLabel(d)}
                                        </option>
                                    );
                                })}
                            </select>
                        </div>

                        <label htmlFor="model" className="control-label">
                            Selected model
                        </label>

                        <div className="controls">
                            <select
                                className="span12"
                                value={selectedModel}
                                name="model"
                                onChange={this.handleFieldChange.bind(this)}
                            >
                                {models.map((d) => {
                                    return (
                                        <option key={d.id} value={d.id}>
                                            {d.name}
                                        </option>
                                    );
                                })}
                            </select>
                        </div>
                    </div>
                    <div className="span8">
                        <label htmlFor="notes" className="control-label">
                            Notes
                        </label>
                        <div className="controls">
                            <textarea
                                className="span12"
                                value={this.state.notes}
                                onChange={this.handleFieldChange.bind(this)}
                                name="notes"
                                rows="5"
                                cols="40"
                            />
                            <p className="help-block">
                                Enter notes on why a model was selected as best fitting; if no model
                                is selected, add notes on why no model was selected.
                            </p>
                        </div>
                    </div>
                </form>
            </div>
        );
    }

    renderWell() {
        return (
            <div className="well" key={1}>
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={this.handleSaveSelected.bind(this)}
                >
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
            <div>
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
