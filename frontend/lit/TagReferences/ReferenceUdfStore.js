import $ from "jquery";
import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

const renderTagForm = function(tagId, referenceId, tagNames, udf) {
    return `<div class='box-shadow rounded mt-3 mb-4'>
        <a
            class="text-black text-decoration-none clickable bg-gray rounded-top px-3 d-flex justify-content-start align-items-center flex-wrap border-bottom-light"
            type="button"
            data-toggle="collapse"
            id="udf-header-${tagId}-${referenceId}"
            data-target="#collapse-${tagId}-${referenceId}-udf"
            aria-expanded="true" aria-controls="collapse-${tagId}-udf">
                <span class="refTag px-1 py-0 my-3">${tagNames[tagId]}</span>
                <span class="h5 m-0">Tag Form</span>
        </a>
        <div class="px-4 py-3 collapse show" id="collapse-${tagId}-${referenceId}-udf">
            ${udf}
        </div>
    </div>`;
};

class UdfStore {
    @observable formHtml = "";
    @observable activeIds = [];
    @observable values = null;
    @observable errors = null;

    constructor(parent) {
        this.parent = parent;
        this.config = parent.config;

        // change udf values whenever reference changes
        autorun(() => {
            this.values = this.parent.reference
                ? this.parent.reference.data.tag_udf_contents
                : null;
        });

        // change form display whenever selected tags change
        autorun(() => {
            if (!this.parent.reference) {
                return;
            }
            const tagIds = this.parent.referenceUserTags.map(tag => tag.data.pk),
                tagNames = this.config.tag_names,
                referenceId = this.referenceId,
                {udfs, descendant_tags} = this.parent.config,
                activeIds = _.keys(udfs).filter(tagId =>
                    descendant_tags[tagId].some(tag => tagIds.includes(tag))
                ),
                tagFormDivs = activeIds
                    .map(tagId => renderTagForm(tagId, referenceId, tagNames, udfs[tagId]))
                    .join("");

            this.activeIds = activeIds;
            this.formHtml = tagFormDivs;
        });
    }

    @computed get referenceId() {
        return this.parent.reference.data.pk;
    }

    @action.bound updateValues() {
        const formData = $("#udf-forms").serializeArray(),
            values = {};
        // Save form data as a dictionary of field-name: field-value pairs
        // This makes it easy to set the form fields in the ReferenceUDF component
        // value is always an array, even for single items
        formData.forEach(
            ({name, value}) =>
                (values[name] = name in values ? values[name].concat(value) : [].concat(value))
        );
        // Overwrite changed fields while keeping data from fields removed from the form;
        // allows users to remove then re-add a tag and use existing UDF data for that tag
        Object.assign(this.values, values);
    }

    @action.bound getSubmissionValues() {
        // set current values to store state; this follows `updateValues` above;
        // return values for submission in a slightly different format for API submission
        const newValuesSubmit = {},
            newValues = {},
            formData = $("#udf-forms").serializeArray();

        this.activeIds.forEach(tagId => {
            newValuesSubmit[tagId] = {};
            formData.forEach(({name, value}) => {
                if (!name.includes(`${tagId}-`)) {
                    return;
                }
                if (name in newValues) {
                    newValues[name] = newValues[name].concat(value);
                    newValuesSubmit[tagId][name] = [value].concat(newValuesSubmit[tagId][name]);
                } else {
                    newValues[name] = [].concat(value);
                    newValuesSubmit[tagId][name] = value;
                }
            });
        });
        this.values = newValues;
        return newValuesSubmit;
    }
}

export default UdfStore;
