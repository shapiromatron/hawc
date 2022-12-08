import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    config = null;
    // a flag used to indicate that state change happened from successful save
    updateFromSave = false;
    @observable tagtree = null;
    @observable references = [];
    @observable reference = null;
    @observable referenceTags = null;
    @observable referenceUserTags = null;
    @observable errorOnSave = false;
    @observable filterClass = "";
    @observable showInstructionsModal = false;
    @observable lastResolved = false;

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
    }
    hasTag(tags, tag) {
        return !!_.find(tags, e => e.data.pk == tag.data.pk);
    }
    @action.bound addTag(tag) {
        if (
            this.hasReference &&
            !_.find(this.referenceUserTags, el => el.data.pk === tag.data.pk)
        ) {
            this.referenceUserTags.push(tag);
        }
    }
    @action.bound removeTag(tag) {
        _.remove(this.referenceUserTags, el => el.data.pk === tag.data.pk);
    }
    @action.bound toggleTag(tag) {
        return this.hasTag(this.referenceUserTags, tag) ? this.removeTag(tag) : this.addTag(tag);
    }
    @action.bound saveAndNext() {
        const payload = {
                pk: this.reference.data.pk,
                tags: this.referenceUserTags.map(tag => tag.data.pk),
            },
            url = `/lit/api/reference/${this.reference.data.pk}/tag/`,
            // since the success function is a promise and makes a number of changes we need to
            // wrap it in a mobx action so that it doesn't count each individual change
            success = action(resolved => {
                const index = _.findIndex(
                    this.references,
                    ref => ref.data.pk === this.reference.data.pk
                );

                this.lastResolved = resolved;
                this.errorOnSave = false;

                this.reference.userTags = toJS(this.referenceUserTags);
                if (!this.config.conflict_resolution) {
                    this.reference.tags = toJS(this.referenceUserTags);
                }
                const nextIndex = this.references.length > index + 1 ? index + 1 : 0,
                    reference = this.references[nextIndex];
                this.setReference(reference);

                this.updateFromSave = true;
            }),
            failure = data => {
                console.error(data);
                this.errorOnSave = true;
            };

        $.post(url, payload, v => (v.status === "success" ? success(v.resolved) : failure())).fail(
            failure
        );
    }
    @action.bound removeAllTags() {
        this.referenceUserTags = [];
    }
    @action.bound toggleSlideAway() {
        this.filterClass = this.filterClass == "" ? "slideAway" : "";
    }
    @action.bound setInstructionsModal(input) {
        this.showInstructionsModal = input;
    }
}

export default Store;
