import React, {Component} from "react";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";
import h from "shared/utils/helpers";
import HAWCUtils from "shared/utils/HAWCUtils";
import FormActions from "shared/components/FormActions";

class BaseVisualForm extends Component {
    constructor(props) {
        super(props);
        this.config = JSON.parse(document.getElementById("config").textContent);
        this.state = {
            title: "",
            slug: "",
            dose_units: null,
            caption: "",
            published: "",
            visual_type: this.config.visual_type,
            settings: "undefined",
            endpoints: [],
            dataRefreshRequired: true,
        };
    }

    componentDidMount() {
        if (this.config.crud == "Update") {
            fetch(`${this.config.data_url}${this.config.instance.id}`, h.fetchGet)
                .then(response => response.json())
                .then(json => {
                    let {title, slug, dose_units, endpoints, settings, caption, published} = json;
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
    }

    handleInputChange = e => {
        this.setState({[e.target.name]: e.target.value, dataRefreshRequired: true});
    };

    handleQuillInputChange = (name, value) => {
        this.setState({[name]: value, dataRefreshRequired: true});
    };

    handleCheckboxChange = e => {
        this.setState({[e.target.name]: e.target.checked, dataRefreshRequired: true});
    };

    handleDoseUnitSelect = value => {
        this.setState({dose_units: parseInt(value), dataRefreshRequired: true});
    };

    handleTitleChange = e => {
        // When creating a new visual, the slug automatically changes w/ the
        // title. However, if updating, the slug does not change automatically.
        let title = e.target.value,
            newState = {
                title,
                dataRefreshRequired: true,
            };

        if (this.config.crud === "Create") {
            newState.slug = HAWCUtils.urlify(title);
        }
        this.setState(newState);
    };

    handleEndpointSelect = value => {
        this.setState({endpoints: value, dataRefreshRequired: true});
    };

    handleTabSelection = tabIndex => {
        // Get new data for chart if a user clicks the preview tab and
        // the data has changed.
        if (tabIndex === 2 && this.state.dataRefreshRequired) {
            fetch(this.config.preview_url, h.fetchForm(this.config.csrf, this.form))
                .then(response => response.json())
                .then(json => this.updatePreviewGraph(json))
                .then(() => this.setState({dataRefreshRequired: false}));
        }
    };

    getEndpointChoices(endpoint) {
        return HAWCUtils.abstractMethod();
    }

    fetchEndpoints = (input, callback) => {
        const url = `${this.config.endpoint_url}?animal_group__experiment__study__assessment_id=${this.config.assessment}&q=${input}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => callback(json.results));
    };

    renderForm() {
        return HAWCUtils.abstractMethod();
    }

    renderSettingsForm() {
        return HAWCUtils.abstractMethod();
    }

    updatePreviewGraph(json) {
        return HAWCUtils.abstractMethod();
    }

    render() {
        return (
            <Tabs onSelect={this.handleTabSelection}>
                <TabList>
                    <Tab>Visualization settings</Tab>
                    <Tab>Figure customization</Tab>
                    <Tab>Preview</Tab>
                </TabList>

                <form ref={form => (this.form = form)} method="POST" id="visualForm">
                    <TabPanel>
                        <input type="hidden" name="csrfmiddlewaretoken" value={this.config.csrf} />
                        <legend>
                            {this.config.crud} {this.state.title}
                        </legend>
                        {this.renderForm()}
                    </TabPanel>
                    <TabPanel>{this.renderSettingsForm()}</TabPanel>
                    <TabPanel forceRender>
                        <div ref={preview => (this.preview = preview)} />
                    </TabPanel>
                    <FormActions isForm={true} cancel={this.config.cancel_url} />
                </form>
            </Tabs>
        );
    }
}

BaseVisualForm.propTypes = {};

export default BaseVisualForm;
