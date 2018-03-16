import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Async } from 'react-select';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import fetch from 'isomorphic-fetch';
import _ from 'lodash';

import 'react-tabs/style/react-tabs.css';
import 'react-select/dist/react-select.css';

import h from 'shared/utils/helpers';
import { splitStartup } from 'utils/WebpackSplit';
import HAWCUtils from 'utils/HAWCUtils';

class BaseVisualForm extends Component {
    constructor(props) {
        super(props);
        this.config = JSON.parse(document.getElementById('config').textContent);
        this.state = {
            title: '',
            slug: '',
            dose_units: null,
            caption: '',
            published: '',
            visual_type: this.config.visual_type,
            settings: '',
            endpoints: [],
            syncData: true,
        };
    }

    componentDidMount() {
        this.fetchFormData();
    }

    handleInputChange = (e) => {
        this.setState({ [e.target.name]: e.target.value, syncData: true });
    };

    handleCheckboxChange = (e) => {
        this.setState({ [e.target.name]: e.target.checked, syncData: true });
    };

    handleDoseUnitSelect = (value) => {
        this.setState({ dose_units: parseInt(value), syncData: true });
    };

    handleEndpointSelect = (value) => {
        this.setState({ endpoints: value, syncData: true });
    };

    handleTabSelection = (tabIndex) => {
        if (tabIndex === 2 && this.state.syncData) {
            fetch(this.config.preview_url, h.fetchForm(this.config.csrf, $(this.form).serialize()))
                .then((response) => response.json())
                .then((json) => this.updatePreviewGraph(json))
                .then(() => this.setState({ syncData: false }));
        }
    };

    getEndpointChoices = (endpoint) => {
        return [];
    };

    fetchFormData = () => {
        if (this.config.crud == 'Update') {
            fetch(`${this.config.data_url}${this.config.instance.id}`, h.fetchGet)
                .then((response) => response.json())
                .then((json) => {
                    let { title, slug, dose_units, endpoints, settings, caption, published } = json;
                    this.setState({
                        title,
                        slug,
                        dose_units,
                        caption,
                        published,
                        visual_type: this.config.visual_type,
                        settings: JSON.stringify(settings),
                        endpoints: this.getEndpointChoices(endpoints),
                    });
                });
        }
    };

    fetchEndpoints = (input, callback) => {
        fetch(
            `${this.config.endpoint_url}?related=${this.config.assessment}&term=${input}`,
            h.fetchGet
        )
            .then((response) => response.json())
            .then((json) => {
                callback(null, { options: json.data });
            });
    };

    renderForm = () => {
        return HAWCUtils.abstractMethod();
    };

    renderSettingsForm = () => {
        return HAWCUtils.abstractMethod();
    };

    updatePreviewGraph = (json) => {
        return HAWCUtils.abstractMethod();
    };

    render() {
        return (
            <Tabs onSelect={this.handleTabSelection}>
                <TabList>
                    <Tab>Visualization settings</Tab>
                    <Tab>Figure customization</Tab>
                    <Tab>Preview</Tab>
                </TabList>

                <form
                    ref={(form) => {
                        this.form = form;
                    }}
                    method="POST"
                >
                    <TabPanel>
                        <input type="hidden" name="csrfmiddlewaretoken" value={this.config.csrf} />
                        <legend>
                            {this.config.crud} {this.state.title}
                        </legend>
                        <p>{this.config.crud} a visualization</p>
                        <br />
                        {this.renderForm()}
                    </TabPanel>
                    <TabPanel>{this.renderSettingsForm()}</TabPanel>
                    <TabPanel forceRender>
                        <div id="preview" />
                    </TabPanel>
                    <div className="form-actions">
                        <input
                            type="submit"
                            name="save"
                            value="Save"
                            className="btn btn-primary"
                            id="submit-id-save"
                        />
                        <a role="button" className="btn btn-default" href={this.config.cancel_url}>
                            Cancel
                        </a>
                    </div>
                </form>
            </Tabs>
        );
    }
}

BaseVisualForm.propTypes = {};

export default BaseVisualForm;

const formRender = (element) => {
    splitStartup(element, BaseVisualForm);
};

export { formRender };
