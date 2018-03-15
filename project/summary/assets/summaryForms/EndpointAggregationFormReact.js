import React from 'react';
import PropTypes from 'prop-types';
import { Async } from 'react-select';

import 'react-tabs/style/react-tabs.css';
import 'react-select/dist/react-select.css';

import BaseVisualForm from './BaseVisualFormReact';
import EndpointAggregation from 'summary/EndpointAggregation';

import { splitStartup } from 'utils/WebpackSplit';
import ArraySelect from 'shared/components/ArraySelect';
import TextInput from 'shared/components/TextInput';
import TextAreaInput from 'shared/components/TextAreaInput';

class EndpointAggregationForm extends BaseVisualForm {
    getEndpointChoices = (endpoints) => {
        return endpoints.map((e) => {
            let s = e.animal_group.experiment.study.short_citation,
                x = e.animal_group.experiment.name,
                g = e.animal_group.name;
            return {
                value: e.id,
                label: `${s} | ${x} | ${g} | ${e.name}`,
            };
        });
    };

    updatePreviewGraph = (json) => {
        new EndpointAggregation(json).displayAsPage($('#preview').empty());
    };

    renderForm = () => {
        let doseUnitChoices = this.config.dose_units.map((u) => {
            return { id: u.id, value: u.name };
        });
        return (
            <div>
                <TextInput
                    name="title"
                    label="Title"
                    value={this.state.title}
                    onChange={this.handleInputChange}
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
                <div className="control-group">
                    <label className="control-label">Dose Units</label>
                    <div className="controls">
                        <ArraySelect
                            name="dose_units"
                            className="span12 select"
                            choices={doseUnitChoices}
                            id="id_dose_units"
                            value={this.state.dose_units}
                            handleSelect={this.handleDoseUnitSelect}
                        />
                    </div>
                </div>
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
                    />
                </div>
                <TextAreaInput
                    name="settings"
                    label="Settings"
                    value={this.state.settings}
                    onChange={this.handleInputChange}
                    required
                />
                <TextAreaInput
                    name="caption"
                    label="Caption"
                    value={this.state.caption}
                    onChange={this.handleInputChange}
                />
                <div id="div_id_published" className="control-group">
                    <div className="controls">
                        <label className="checkbox">
                            <input
                                onChange={this.handleCheckboxChange}
                                type="checkbox"
                                name="published"
                                className="checkboxinput"
                                id="id_published"
                                checked={this.state.published}
                            />
                            Publish visual for public viewing
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
        return null;
    };
}

EndpointAggregationForm.propTypes = {};

export default EndpointAggregationForm;

const formRender = (element) => {
    splitStartup(element, EndpointAggregationForm);
};

class EndpointAggregationShim {
    constructor(element) {
        formRender(element);
    }
}
export { formRender, EndpointAggregationShim };
