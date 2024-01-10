import $ from "jquery";
import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

import Reference from "../Reference";
import TagTree from "../TagTree";

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

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.array(config.refs, this.tagtree, false);
        // set first reference
        if (this.references.length > 0) {
            this.setReference(this.references[0]);
        }
    }
    @computed get hasReference() {
        return this.reference !== null;
    }
    @action.bound setReference(reference) {
        this.reference = reference;
        this.referenceTags = reference.tags.slice(0); // shallow copy
        this.referenceUserTags = reference.userTags
            ? reference.userTags.slice(0)
            : reference.tags.slice(0);
        this.setUDF();
        this.UDFValues = this.reference.data.tag_udf_contents;
    }
    @action.bound setUDF() {
        const intersects = (a, b) => a.some(x => b.includes(x));
        const referenceUserTagIDs = this.referenceUserTags.map(tag => tag.data.pk);
        var udfHTML = "";
        this.udfIDs = [];
        if (this.config.udfs) {
            for (const [tagID, udf] of Object.entries(this.config.udfs)) {
                if (intersects(this.config.descendant_tags[tagID], referenceUserTagIDs)) {
                    udfHTML += udf;
                    this.udfIDs.push(tagID);
                }
            }
        }
        this.currentUDF = udfHTML;
    }
    @action.bound getFinalUDFValues() {
        var newValuesSubmit = {};
        for (const tagID of this.udfIDs) {
            newValuesSubmit[tagID] = {};
            $(`input[name*='${tagID}-']`).each(function() {
                var field = $(this)
                    .attr("name")
                    .substring(tagID.length + 1);
                newValuesSubmit[tagID][`${tagID}-${field}`] = $(this).val();
            });
        }
        return newValuesSubmit;
    }
    @action.bound recordUDFValues(final = false) {
        var newValuesLocal = {};
        var newValuesSubmit = {};
        for (const tagID of this.udfIDs) {
            newValuesLocal[tagID] = {};
            newValuesSubmit[tagID] = {};
            $(`input[name*='${tagID}-']`).each(function() {
                var field = $(this)
                    .attr("name")
                    .substring(tagID.length + 1);
                newValuesLocal[tagID][field] = $(this).val();
                newValuesSubmit[tagID][`${tagID}-${field}`] = $(this).val();
            });
        }
        final ? (this.UDFValues = newValuesLocal) : Object.assign(this.UDFValues, newValuesLocal);
        return newValuesSubmit;
    }
    hasTag(tags, tag) {
        return !!_.find(tags, e => e.data.pk == tag.data.pk);
    }
    @action.bound addTag(tag) {
        this.recordUDFValues();
        if (
            this.hasReference &&
            !_.find(this.referenceUserTags, el => el.data.pk === tag.data.pk)
        ) {
            this.referenceUserTags.push(tag);
        }
        this.setUDF();
    }
    @action.bound removeTag(tag) {
        this.recordUDFValues();
        _.remove(this.referenceUserTags, el => el.data.pk === tag.data.pk);
        this.setUDF();
    }
    @action.bound toggleTag(tag) {
        return this.hasTag(this.referenceUserTags, tag) ? this.removeTag(tag) : this.addTag(tag);
    }
    @action.bound handleSaveSuccess(response) {
        const {resolved} = response;
        this.errorOnSave = false;
        this.reference.userTags = resolved ? null : toJS(this.referenceUserTags);
        this.reference.data.tag_udf_contents = toJS(this.UDFValues);
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
    @action.bound handleSaveFailure() {
        this.errorOnSave = true;
    }
    @action.bound saveAndNext() {
        this.successMessage = "";
        this.errorOnSave = false;
        const payload = {
                pk: this.reference.data.pk,
                tags: this.referenceUserTags.map(tag => tag.data.pk),
                udf_data: this.recordUDFValues(true),
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
        this.recordUDFValues();
        this.setUDF();
    }
    @action.bound toggleSlideAway() {
        this.filterClass = this.filterClass == "" ? "slideAway" : "";
    }
    @action.bound setInstructionsModal(input) {
        this.showInstructionsModal = input;
    }
}

export default Store;
