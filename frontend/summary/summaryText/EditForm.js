import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import NonFieldErrors from "shared/components/NonFieldErrors";
import QuillTextInput from "shared/components/QuillTextInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import HAWCUtils from "shared/utils/HAWCUtils";

@inject("store")
@observer
class EditForm extends Component {
    render() {
        const {formData, formErrors, updateFormData, isCreating, parentChoices, siblingChoices} =
            this.props.store;
        return (
            <form>
                <NonFieldErrors errors={formErrors.non_field_errors} />
                <div className="form-row">
                    <div className="col-md-6">
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
                    </div>
                    <div className="col-md-6">
                        <TextInput
                            name="slug"
                            label="Slug"
                            value={formData.slug}
                            errors={formErrors.slug}
                            onChange={e => updateFormData(e.target.name, e.target.value)}
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="col-md-12">
                        <QuillTextInput
                            name="text"
                            label="Text"
                            value={formData.text}
                            errors={formErrors.text}
                            onChange={value => updateFormData("text", value)}
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="col-md-6">
                        <SelectInput
                            name="parent"
                            label="Parent"
                            choices={parentChoices}
                            multiple={false}
                            value={formData.parent}
                            errors={formErrors.parent}
                            handleSelect={value => updateFormData("parent", parseInt(value))}
                        />
                    </div>
                    <div className="col-md-6">
                        <SelectInput
                            name="sibling"
                            label="Insert after"
                            choices={siblingChoices}
                            multiple={false}
                            value={formData.sibling}
                            errors={formErrors.sibling}
                            handleSelect={value =>
                                updateFormData("sibling", parseInt(value) || null)
                            }
                        />
                    </div>
                </div>
            </form>
        );
    }
}

EditForm.propTypes = {
    store: PropTypes.object,
};

export default EditForm;
