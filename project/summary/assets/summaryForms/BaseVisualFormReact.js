import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Async, Option } from 'react-select';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import fetch from 'isomorphic-fetch';
import _ from 'lodash';

import 'react-tabs/style/react-tabs.css';
import 'react-select/dist/react-select.css';

import h from 'shared/utils/helpers';
import { splitStartup } from 'utils/WebpackSplit';
import ArraySelect from 'shared/components/ArraySelect';
import TextInput from 'shared/components/TextInput';
import TextAreaInput from 'shared/components/TextAreaInput';
import HAWCUtils from 'utils/HAWCUtils';

class BaseVisualForm extends Component {
    constructor(props) {
        super(props);
        this.config = JSON.parse(document.getElementById('config').textContent);
        let { title, slug, dose_units, endpoints, settings, caption, published } = this.config.instance;
        this.state = {
            title,
            slug,
            dose_units,
            caption,
            published,
            settings: JSON.stringify(settings),
            endpoints: endpoints.map((e) => {
                let s = e.animal_group.experiment.study.short_citation,
                    x = e.animal_group.experiment.name,
                    g = e.animal_group.name;
                return {
                    value: e.id,
                    label: `${s} | ${x} | ${g} | ${e.name}`}})
        }
        console.log('this.config', this.config);
    }

    handleInputChange = (e) => {
        this.setState({[e.target.name]: e.target.value})
    }

    handleCheckboxChange = (e) => {
        this.setState({[e.target.name]: e.target.checked})
    }

    handleDoseUnitSelect = (value) => {
        this.setState({ dose_units: parseInt(value) })
    }

    handleEndpointSelect = (value) => {
        this.setState({ endpoints: value });
    }

    fetchEndpoints = (input, callback) => {
        fetch(`${this.config.endpointUrl}?related=${this.config.instance.assessment}&therm=${input}`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => {
                callback(null, { options: json.data});
            });
    }

    onSubmit = (e) => {

    }

    render() {
        let doseUnitChoices = this.config.dose_units.map((u) => { return { id: u.id, value: u.name}; });
        return (
            <Tabs>
                <TabList>
                    <Tab>Visualization settings</Tab>
                    <Tab>Figure customization</Tab>
                    <Tab>Preview</Tab>
                </TabList>

                <TabPanel>
                    <form method="POST" id="visualForm">
                        <input type="hidden" name='csrfmiddlewaretoken' value={this.config.csrf}/>
                        <legend>Update {this.state.title}</legend>
                        <p>Update an existing visualization</p>
                        <br/>
                        <TextInput
                            name='title'
                            label='Title'
                            value={this.state.title}
                            onChange={this.handleInputChange}
                            required
                        />
                        <TextInput
                            name='slug'
                            label='URL Name'
                            value={this.state.slug}
                            onChange={this.handleInputChange}
                            helpText='The URL (web address) used to describe this object (no spaces or special-characters).'
                            required
                        />
                        <div className="control-group">
                            <label className="control-label">
                                Dose Units
                            </label>
                            <div className="controls">
                                <ArraySelect
                                    name='dose_units'
                                    className='span12 select'
                                    choices={doseUnitChoices}
                                    id='id_dose_units'
                                    defVal={this.state.dose_units}
                                    handleSelect={this.handleDoseUnitSelect}
                                />
                            </div>

                        </div>
                        <div className='control-group'>
                            <label className='control-label'>
                                Endpoints
                                <span className="asteriskField">*</span>
                            </label>
                            <Async
                                multi
                                name='endpoints'
                                value={this.state.endpoints}
                                onChange={this.handleEndpointSelect}
                                loadOptions={this.fetchEndpoints}
                                backspaceRemoves={false}
                                deleteRemoves={false}
                                clearable={false}
                            />
                        </div>
                        <TextAreaInput
                            name='settings'
                            label='Settings'
                            value={this.state.settings}
                            onChange={this.handleInputChange}
                            required
                        />
                        <TextAreaInput
                            name='caption'
                            label='Caption'
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
                                <p id="hint_id_published" className="help-block">For assessments marked for public viewing, mark visual to be viewable by public</p>
                            </div>
                        </div>
                        <div className="form-actions">
                            <input type="submit" name="save" value="Save" className="btn btn-primary" id="submit-id-save" onSubmit={this.onSubmit} />
                            <a role="button" className="btn btn-default" href="/summary/visual/1/">Cancel</a>
                        </div>
                    </form>
                </TabPanel>
                <TabPanel>
                    <h2>Any content 2</h2>
                </TabPanel>
                <TabPanel>
                    <h2>Any content 3</h2>
                </TabPanel>
            </Tabs>
        );
    }
}

BaseVisualForm.propTypes = {

};

export default BaseVisualForm;

const formRender =  (element) => {
    splitStartup(element, BaseVisualForm);
};

export { formRender };
