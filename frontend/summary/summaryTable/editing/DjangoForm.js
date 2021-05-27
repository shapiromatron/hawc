import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import HAWCUtils from "utils/HAWCUtils";
import TextInput from "shared/components/TextInput";
import TextAreaInput from "shared/components/TextAreaInput";
import CheckboxInput from "shared/components/CheckboxInput";

@inject("store")
@observer
class DjangoForm extends Component {
    render() {
        const {
                formErrors,
                tableObject,
                isCreate,
                updateContent,
                updateTableContent,
                handleSubmit,
                cancelUrl,
            } = this.props.store,
            header = isCreate ? "Create new table" : `Update ${tableObject.title}`,
            helpText = isCreate ? "..." : "Update an existing table",
            saveBtnText = isCreate ? "Create" : "Update";

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
                <div className="form-actions">
                    <button type="button" onClick={handleSubmit} className="btn btn-primary mr-1">
                        {saveBtnText}
                    </button>
                    <a href={cancelUrl} className="btn btn-light">
                        Cancel
                    </a>
                </div>
            </div>
        );
    }
}

DjangoForm.propTypes = {
    store: PropTypes.object,
};

export default DjangoForm;
