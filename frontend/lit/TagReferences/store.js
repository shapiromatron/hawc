import $ from "jquery";
import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

import Reference from "../Reference";
import TagTree from "../TagTree";
import UdfStore from "./ReferenceUdfStore";

class Store {
    config = null;
    @observable tagtree = null;
    @observable references = [];
    @observable reference = null;
    @observable referenceTags = null;
    @observable referenceUserTags = null;
    @observable errorOnSave = false;
    @observable successMessage = "";
    @observable filterClass = "";
    @observable showInstructionsModal = false;
    @observable currentUDF = null;
    @observable UDFValues = null;
    @observable UDFError = null;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.tagNames = config.tag_names;
        this.references = Reference.array(config.refs, this.tagtree, false);
        this.udfStore = new UdfStore(this);
        // set first reference
        if (this.references.length > 0) {
            this.setReference(this.references[0]);
        }
    }
    @computed get hasReference() {
        return this.reference !== null;
    }
    @action.bound resetReferenceErrors() {
        this.errorOnSave = false;
        this.udfStore.errors = null;
    }
    @action.bound setReference(reference) {
        this.resetReferenceErrors();
        this.reference = reference;
        this.referenceTags = reference.tags.slice(0); // shallow copy
        this.referenceUserTags = reference.userTags
            ? reference.userTags.slice(0)
            : reference.tags.slice(0);
        this.currentUDF = null;
        this.setUDF();
        this.UDFValues = this.reference.data.tag_udf_contents;
        this.UDFError = null;
        this.errorOnSave = false;
    }
    @action.bound setUDF() {
        const referenceUserTagIDs = this.referenceUserTags.map(tag => tag.data.pk);
        var udfHTML = "";
        this.udfIDs = []; // reset current UDF tag IDs
        if (this.config.udfs) {
            // check all tag UDFs for the assessment
            for (const [tagID, udf] of Object.entries(this.config.udfs)) {
                // if any descendant of the UDF tag is on the reference
                if (
                    this.config.descendant_tags[tagID].some(tag =>
                        referenceUserTagIDs.includes(tag)
                    )
                ) {
                    udfHTML += `<div class='box-shadow rounded mt-3 mb-4'>
                                    <a class="text-black text-decoration-none clickable bg-gray
                                        rounded-top px-3 d-flex justify-content-start
                                        align-items-center flex-wrap border-bottom-light"
                                        type="button" data-toggle="collapse" id="udf-header-${tagID}-${this.reference.data.pk}"
                                        data-target="#collapse-${tagID}-${this.reference.data.pk}-udf"
                                        aria-expanded="true" aria-controls="collapse-${tagID}-udf">
                                            <span class="refTag px-1 py-0 my-3">${this.tagNames[tagID]}</span>
                                            <span class="h5 m-0">Tag Form</span>
                                    </a>
                                <div class="px-4 py-3 collapse show" id="collapse-${tagID}-${this.reference.data.pk}-udf">${udf}</div></div>`;
                    this.udfIDs.push(tagID); // add to current UDF tag ids list
                }
            }
        }
        this.currentUDF = udfHTML;
    }
    @action.bound recordUDFValues() {
        var newValues = {};
        // Save form data as a dictionary of field-name: field-value pairs
        // This makes it easy to set the form fields in the ReferenceUDF component
        _.each($("#udf-form").serializeArray(), function(field) {
            newValues[field["name"]] =
                field["name"] in newValues
                    ? newValues[field["name"]].concat(field["value"])
                    : [].concat(field["value"]);
        });
        // Using dictionary means we can overwrite changed fields while keeping data from fields removed from the form
        // this allows a user to remove and readd a tag and still use existing UDF data for that tag
        Object.assign(this.UDFValues, newValues);
    }
    @action.bound getFinalUDFValues() {
        var newValuesSubmit = {};
        var newValues = {};
        for (const tagID of this.udfIDs) {
            newValuesSubmit[tagID] = {};
            for (const field of $("#udf-form").serializeArray()) {
                if (field["name"].includes(`${tagID}-`)) {
                    if (field["name"] in newValues) {
                        newValues[field["name"]] = newValues[field["name"]].concat(field["value"]);
                        newValuesSubmit[tagID][field["name"]] = [field["value"]].concat(
                            newValuesSubmit[tagID][field["name"]]
                        );
                    } else {
                        newValues[field["name"]] = [].concat(field["value"]);
                        newValuesSubmit[tagID][field["name"]] = field["value"];
                    }
                }
            }
        }
        // here we overwrite the local values with the final saved data instead of using Object.assign (see recordUDFvalues() above)
        this.UDFValues = newValues;
        return newValuesSubmit;
    }
    hasTag(tags, tag) {
        return !!_.find(tags, e => e.data.pk == tag.data.pk);
    }
    @action.bound addTag(tag) {
        this.udfStore.updateValues();
        if (
            this.hasReference &&
            !_.find(this.referenceUserTags, el => el.data.pk === tag.data.pk)
        ) {
            this.referenceUserTags.push(tag);
        }
        this.setUDF();
    }
    @action.bound removeTag(tag) {
        this.udfStore.updateValues();
        _.remove(this.referenceUserTags, el => el.data.pk === tag.data.pk);
        this.setUDF();
    }
    @action.bound toggleTag(tag) {
        return this.hasTag(this.referenceUserTags, tag) ? this.removeTag(tag) : this.addTag(tag);
    }
    @action.bound handleSaveSuccess(response) {
        const {resolved} = response;
        this.resetReferenceErrors();
        this.reference.userTags = resolved ? null : toJS(this.referenceUserTags);
        this.reference.data.tag_udf_contents = toJS(this.udfStore.values);
        if (!this.config.conflict_resolution || resolved) {
            this.reference.tags = toJS(this.referenceUserTags);
        }
        window.setTimeout(
            action(() => {
                const index = _.findIndex(
                        this.references,
                        ref => ref.data.pk === this.reference.data.pk
                    ),
                    nextIndex = this.references.length > index + 1 ? index + 1 : 0,
                    reference = this.references[nextIndex];
                this.successMessage = "";
                this.setReference(reference);
            }),
            1000
        );
        this.successMessage = resolved ? "Saved! Tags added with no conflict." : "Saved!";
    }
    @action.bound handleSaveFailure(response) {
        this.udfStore.errors = response["UDF-form"] || null;
        this.errorOnSave = true;
    }
    @action.bound saveAndNext() {
        this.successMessage = "";
        this.resetReferenceErrors();
        const payload = {
                pk: this.reference.data.pk,
                tags: this.referenceUserTags.map(tag => tag.data.pk),
                udf_data: this.udfStore.getSubmissionValues(),
            },
            url = `/lit/api/reference/${this.reference.data.pk}/tag/`;
        h.handleSubmit(
            url,
            "POST",
            this.config.csrf,
            payload,
            this.handleSaveSuccess,
            this.handleSaveFailure,
            this.handleSaveFailure
        );
    }
    @action.bound removeAllTags() {
        this.referenceUserTags = [];
        this.udfStore.updateValues();
    }
    @action.bound toggleSlideAway() {
        this.filterClass = this.filterClass == "" ? "slideAway" : "";
    }
    @action.bound setInstructionsModal(input) {
        this.showInstructionsModal = input;
    }
}

export default Store;
