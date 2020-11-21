import _ from "lodash";
import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import HAWCUtils from "utils/HAWCUtils";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";
import QuillTextInput from "shared/components/QuillTextInput";

@inject("store")
@observer
class EditForm extends Component {
    render() {
        const {formData, formErrors, updateFormData, isCreating} = this.props.store;
        return (
            <form>
                <TextInput
                    name="title"
                    helpText="Section heading name"
                    label="Title"
                    value={formData.title}
                    errors={formErrors.title}
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
                    errors={formErrors.slug}
                    onChange={e => updateFormData(e.target.name, e.target.value)}
                />
                <QuillTextInput
                    name="text"
                    label="Text"
                    value={formData.text}
                    errors={formErrors.text}
                    onChange={value => updateFormData("text", value)}
                />
                <SelectInput
                    name="parent"
                    label="Parent"
                    choices={[
                        {id: "---", label: "<root>"},
                        {id: "foo", label: "foo"},
                    ]}
                    multiple={false}
                    value={formData.parent}
                    errors={formErrors.parent}
                    handleSelect={value => updateFormData("parent", value)}
                />
                <SelectInput
                    name="sibling"
                    label="Sibling"
                    choices={[
                        {id: "---", label: "<root>"},
                        {id: "foo", label: "foo"},
                    ]}
                    multiple={false}
                    value={formData.sibling}
                    errors={formErrors.sibling}
                    handleSelect={value => updateFormData("sibling", value)}
                />
            </form>
        );
    }
}

EditForm.propTypes = {
    store: PropTypes.object,
};

export default EditForm;
