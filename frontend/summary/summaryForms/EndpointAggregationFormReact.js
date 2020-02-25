import $ from "$";
import React from "react";
import {Async} from "react-select";

import "react-tabs/style/react-tabs.css";
import "react-select/dist/react-select.css";

import BaseVisualForm from "./BaseVisualFormReact";
import EndpointAggregation from "summary/summary/EndpointAggregation";

import {splitStartup} from "utils/WebpackSplit";
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
            return {id: u.id, value: u.name};
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
                    className="span12 select"
                    choices={doseUnitChoices}
                    multiple={false}
                    id="id_dose_units"
                    value={this.state.dose_units}
                    handleSelect={this.handleDoseUnitSelect}
                />
                <div className="control-group">
                    <label className="control-label">
                        Endpoints
                        <span className="asteriskField">*</span>
                    </label>
                    <Async
                        multi
                        name="endpoints"
                        value={this.state.endpoints}
                        onChange={this.handleEndpointSelect}
                        autoload={false}
                        loadOptions={this.fetchEndpoints}
                        backspaceRemoves={false}
                        deleteRemoves={false}
                        clearable={false}
                        onValueClick={ep => window.open(`/ani/endpoint/${ep.value}`, "_blank")}
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
                    name="caption"
                    label="Caption"
                    value={this.state.caption}
                    onChange={this.handleInputChange}
                />
                <div id="div_id_published" className="control-group">
                    <div className="controls">
                        <label htmlFor="id_published" className="checkbox">
                            Publish visual for public viewing
                            <input
                                onChange={this.handleCheckboxChange}
                                type="checkbox"
                                name="published"
                                className="checkboxinput"
                                id="id_published"
                                checked={this.state.published}
                            />
                        </label>
                        <p id="hint_id_published" className="help-block">
                            For assessments marked for public viewing, mark visual to be viewable by
                            public
                        </p>
                    </div>
                </div>
            </div>
        );
    };

    renderSettingsForm = () => {
        return (
            <div>
                <p className="help-block">No figure customization settings are available.</p>
            </div>
        );
    };
}

EndpointAggregationForm.propTypes = {};

export default EndpointAggregationForm;

const formRender = element => {
    splitStartup(element, EndpointAggregationForm);
};

// Shim class is for rendering using current VisualForm.create().
// Once all visual forms are refactored, the shim can be removed and formRender used.
class EndpointAggregationShim {
    constructor(element) {
        formRender(element[0]);
    }
}
export {formRender, EndpointAggregationShim};
