import _ from "lodash";
import {action, observable, toJS} from "mobx";

import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    config = null;
    // a flag used to indicate that state change happened from successful save
    updateFromSave = false;
    @observable tagtree = null;
    @observable references = [];
    @observable selectedReference = null;
    @observable selectedReferenceTags = null;
    @observable selectedReferenceUserTags = null;
    @observable errorOnSave = false;
    @observable filterClass = "";
    @observable showInstructionsModal = false;
    @observable lastResolved = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.array(config.refs, this.tagtree);
        // set first reference
        if (this.references.length > 0) {
            this.changeSelectedReference(this.references[0]);
        }
    }

    @action.bound changeSelectedReference(reference) {
        this.selectedReference = reference;
        this.selectedReferenceTags = reference.tags.slice(0); // shallow copy
        this.selectedReferenceUserTags = reference.userTags.slice(0);
    }
    @action.bound addTag(tag) {
        if (
            this.selectedReference &&
            !_.find(
                this.config.conflict_resolution
                    ? this.selectedReferenceUserTags
                    : this.selectedReferenceTags,
                el => el.data.pk === tag.data.pk
            )
        ) {
            this.config.conflict_resolution
                ? this.selectedReferenceUserTags.push(tag)
                : this.selectedReferenceTags.push(tag);
        }
    }
    @action.bound removeTag(tag) {
        _.remove(
            this.config.conflict_resolution
                ? this.selectedReferenceUserTags
                : this.selectedReferenceTags,
            el => el.data.pk === tag.data.pk
        );
    }
    @action.bound saveAndNext() {
        const payload = {
                pk: this.selectedReference.data.pk,
                tags: this.config.conflict_resolution
                    ? this.selectedReferenceUserTags.map(tag => tag.data.pk)
                    : this.selectedReferenceTags.map(tag => tag.data.pk),
            },
            // since the success function is a promise and makes a number of changes we need to
            // wrap it in a mobx action so that it doesn't count each individual change
            success = action(resolved => {
                const index = _.findIndex(
                    this.references,
                    ref => ref.data.pk === this.selectedReference.data.pk
                );

                this.lastResolved = resolved;
                this.errorOnSave = false;

                this.selectedReference.tags = toJS(this.selectedReferenceTags);
                this.selectedReference.userTags = toJS(this.selectedReferenceUserTags);
                this.references.splice(index, 1, toJS(this.selectedReference));
                this.selectedReference = null;
                this.selectedReferenceTags = null;
                this.selectedReferenceUserTags = null;
                if (this.references.length > index + 1) {
                    this.changeSelectedReference(this.references[index + 1]);
                } else {
                    this.changeSelectedReference(this.references[0]);
                }

                this.updateFromSave = true;
            }),
            failure = data => {
                console.error(data);
                this.errorOnSave = true;
            };

        // we wrap the successful
        $.post(`/lit/api/reference/${this.selectedReference.data.pk}/tag/`, payload, v =>
            v.status === "success" ? success(v.resolved) : failure()
        ).fail(failure);
    }
    @action.bound removeAllTags() {
        this.config.conflict_resolution
            ? (this.selectedReferenceUserTags = [])
            : (this.selectedReferenceTags = []);
    }

    @action.bound toggleSlideAway() {
        this.filterClass = this.filterClass == "" ? "slideAway" : "";
    }

    @action.bound setInstructionsModal(input) {
        this.showInstructionsModal = input;
    }
}

export default Store;
