import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Alert from "shared/components/Alert";
import CheckboxInput from "shared/components/CheckboxInput";
import QuillTextInput from "shared/components/QuillTextInput";
import TextAreaInput from "shared/components/TextAreaInput";
import TextInput from "shared/components/TextInput";
import HAWCUtils from "shared/utils/HAWCUtils";

@inject("store")
@observer
class DjangoForm extends Component {
    render() {
        const {formErrors, tableObject, isCreate, updateContent, updateTableContent} =
                this.props.store,
            header = isCreate ? "Create new table" : `Update ${tableObject.title}`,
            helpText = isCreate ? "..." : "Update an existing table";

        return (
            <div>
                <legend>{header}</legend>
                <p className="form-text text-muted">{helpText}</p>
                <TextInput
                    name="title"
                    label="Title"
                    value={tableObject.title}
                    onChange={e => {
                        updateContent(e.target.name, e.target.value);
                        if (isCreate) {
                            updateContent("slug", HAWCUtils.urlify(e.target.value));
                        }
                    }}
                    helpText="Enter the title of the visualization (spaces and special-characters allowed). Eg., Hepatic Effects of Oral [Chemical] Exposure"
                    errors={formErrors.title}
                    required
                />
                <TextInput
                    name="slug"
                    label="URL Name"
                    value={tableObject.slug}
                    onChange={e => updateContent(e.target.name, HAWCUtils.urlify(e.target.value))}
                    helpText="The URL (web address) used to describe this object (no spaces or special-characters)."
                    errors={formErrors.slug}
                    required
                />
                <QuillTextInput
                    name="caption"
                    label="Caption"
                    value={tableObject.caption}
                    onChange={value => updateContent("caption", value)}
                    errors={formErrors.caption}
                />
                <TextAreaInput
                    name="content"
                    label="Table content"
                    value={tableObject.content}
                    onChange={e => updateTableContent(e.target.value, true)}
                    helpText="Advanced users only - paste from another table to copy content (or leave as is this is controlled by other fields)."
                    errors={formErrors.content}
                    required
                />
                <CheckboxInput
                    name="published"
                    label="Publish for public viewing"
                    checked={tableObject.published}
                    onChange={e => updateContent(e.target.name, e.target.checked)}
                    errors={formErrors.published}
                    helpText="If published (and your assessment is public), the table can be viewed by the public"
                />
                {formErrors.non_field_errors ? (
                    <Alert message={formErrors.non_field_errors} />
                ) : null}
            </div>
        );
    }
}

DjangoForm.propTypes = {
    store: PropTypes.object,
};

export default DjangoForm;
