import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import QuillTextInput from "shared/components/QuillTextInput";
import TextAreaInput from "shared/components/TextAreaInput";
import TextInput from "shared/components/TextInput";
import HAWCUtils from "shared/utils/HAWCUtils";

@inject("store")
@observer
class OverallPanel extends Component {
    render() {
        const {isCreate, djangoFormData, updateDjangoFormData} = this.props.store.base;
        return (
            <div>
                <legend>Prisma Settings</legend>
                <p className="form-text text-muted">....</p>
                <TextInput
                    name="title"
                    label="Title"
                    value={djangoFormData.title}
                    onChange={e => {
                        updateDjangoFormData(e.target.name, e.target.value);
                        if (isCreate) {
                            updateDjangoFormData("slug", HAWCUtils.urlify(e.target.value));
                        }
                    }}
                    required
                />
                <TextInput
                    name="slug"
                    label="URL Name"
                    value={djangoFormData.slug}
                    onChange={e => updateDjangoFormData(e.target.name, e.target.value)}
                    helpText="The URL (web address) used to describe this object (no spaces or special-characters)."
                    required
                />
                <TextAreaInput
                    name="settings"
                    label="Settings"
                    value={djangoFormData.settings}
                    onChange={e => updateDjangoFormData(e.target.name, e.target.value)}
                    helpText='Paste from another visualization to copy settings, or set to "undefined".'
                    required
                />
                <QuillTextInput
                    name="caption"
                    label="Caption"
                    value={djangoFormData.caption}
                    onChange={value => updateDjangoFormData("caption", value)}
                />
                <CheckboxInput
                    name="published"
                    label="Publish visual for public viewing"
                    checked={djangoFormData.published}
                    onChange={e => updateDjangoFormData(e.target.name, e.target.checked)}
                    helpText="For assessments marked for public viewing, mark visual to be viewable by public"
                />
            </div>
        );
    }
}
OverallPanel.propTypes = {
    store: PropTypes.object,
};
export default OverallPanel;
