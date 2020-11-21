import _ from "lodash";
import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import HAWCUtils from "utils/HAWCUtils";
import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";

@inject("store")
@observer
class EditForm extends Component {
    render() {
        const {formData, updateFormData, isCreating} = this.props.store;
        return (
            <form>
                <TextInput
                    name="title"
                    label="Title"
                    value={formData.title}
                    onChange={e => {
                        updateFormData(e.target.name, e.target.value);
                        if (isCreating) {
                            updateFormData("slug", HAWCUtils.urlify(e.target.value));
                        }
                    }}
                />
                <TextInput
                    name="slug"
                    label="Slug"
                    value={formData.slug}
                    onChange={e => updateFormData(e.target.name, e.target.value)}
                />
                <QuillTextInput
                    name="text"
                    label="Text"
                    value={formData.text}
                    onChange={value => updateFormData("text", value)}
                />
            </form>
        );
    }
}

EditForm.propTypes = {
    store: PropTypes.object,
};

export default EditForm;
