import _ from "lodash";
import $ from "$";
import React from "react";
import {render} from "react-dom";
import AsyncSelect from "react-select/async";
import BaseVisualForm from "./BaseVisualFormReact";
import EndpointAggregation from "summary/summary/EndpointAggregation";

import QuillTextInput from "shared/components/QuillTextInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import TextAreaInput from "shared/components/TextAreaInput";

class EndpointAggregationForm extends BaseVisualForm {
    getEndpointChoices = endpoints => {
        return endpoints.map(e => {
            let s = e.animal_group.experiment.study.short_citation,
                x = e.animal_group.experiment.name,
                g = e.animal_group.name;
            return {
                value: e.id,
                label: `${s} | ${x} | ${g} | ${e.name}`,
            };
        });
    };

    updatePreviewGraph = json => {
        new EndpointAggregation(json).displayAsPage($(this.preview).empty());
    };

    renderForm = () => {
        let doseUnitChoices = this.config.dose_units.map(u => {
            return {id: u.id, label: u.name};
        });

        return (
            <div>
                <TextInput
                    name="title"
                    label="Title"
                    value={this.state.title}
                    onChange={this.handleTitleChange}
                    required
                />
                <TextInput
                    name="slug"
                    label="URL Name"
                    value={this.state.slug}
                    onChange={this.handleInputChange}
                    helpText="The URL (web address) used to describe this object (no spaces or special-characters)."
                    required
                />
                <SelectInput
                    name="dose_units"
                    label="Dose Units"
                    choices={doseUnitChoices}
                    multiple={false}
                    id="id_dose_units"
                    value={this.state.dose_units}
                    handleSelect={this.handleDoseUnitSelect}
                />
                <div className="form-group">
                    <label className="col-form-label">
                        Endpoints
                        <span className="asteriskField">*</span>
                    </label>
                    <AsyncSelect
                        cacheOptions
                        isMulti
                        name="endpoints"
                        loadOptions={_.debounce(this.fetchEndpoints, 500)}
                        getOptionLabel={opt => opt.text}
                        getOptionValue={opt => opt.id}
                        value={this.state.endpoints}
                        onChange={this.handleEndpointSelect}
                    />
                </div>
                <TextAreaInput
                    name="settings"
                    label="Settings"
                    value={this.state.settings}
                    onChange={this.handleInputChange}
                    helpText='Paste from another visualization to copy settings, or set to "undefined".'
                    required
                />
                <QuillTextInput
                    id="id_caption"
                    name="caption"
                    label="Caption"
                    value={this.state.caption}
                    onChange={value => {
                        this.handleQuillInputChange("caption", value);
                    }}
                />
                <div className="form-group form-check">
                    <input
                        className="form-check-input"
                        onChange={e => this.setState({published: e.target.checked})}
                        type="checkbox"
                        name="published"
                        id="isPublished"
                        checked={this.state.published}
                    />
                    <label htmlFor="isPublished" className="form-check-label">
                        Publish visual for public viewing
                    </label>
                    <small className="form-text text-muted">
                        For assessments marked for public viewing, mark visual to be viewable by
                        public
                    </small>
                </div>
            </div>
        );
    };

    renderSettingsForm = () => {
        return (
            <div>
                <p className="form-text text-muted">
                    No figure customization settings are available.
                </p>
            </div>
        );
    };
}

EndpointAggregationForm.propTypes = {};

export default EndpointAggregationForm;

// Shim class is for rendering using current VisualForm.create().
// Once all visual forms are refactored, the shim can be removed and formRender used.
class EndpointAggregationShim {
    constructor(element) {
        render(<EndpointAggregationForm data={{}} />, element[0]);
    }
}
export {EndpointAggregationShim};
