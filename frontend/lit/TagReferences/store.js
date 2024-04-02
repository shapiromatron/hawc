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

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
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
        this.reference = reference;
        this.referenceTags = reference.tags.slice(0); // shallow copy
        this.referenceUserTags = reference.userTags
            ? reference.userTags.slice(0)
            : reference.tags.slice(0);

        this.resetReferenceErrors();
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
    }
    @action.bound removeTag(tag) {
        this.udfStore.updateValues();
        _.remove(this.referenceUserTags, el => el.data.pk === tag.data.pk);
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
