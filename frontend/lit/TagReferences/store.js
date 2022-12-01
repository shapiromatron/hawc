import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import {sortReferences} from "../constants";
import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    config = null;
    saveIndicatorElement = null;
    @observable tagtree = null;
    @observable references = [];
    @observable selectedReference = null;
    @observable selectedReferenceTags = null;
    @observable selectedReferenceUserTags = null;
    @observable errorOnSave = false;
    @observable filterClass = "";
    @observable showInstructionsModal = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.array(config.refs, this.tagtree);
        // set first reference
        if (this.references.length > 0) {
            this.changeSelectedReference(this.references[0]);
        }
    }

    @computed get workingTags() {
        return this.config.conflict_resolution
            ? this.selectedReferenceUserTags
            : this.selectedReferenceTags;
    }
    @action.bound changeSelectedReference(reference) {
        this.selectedReference = reference;
        this.selectedReferenceTags = reference.tags.slice(0); // shallow copy
        // user tags should default to the current consensus tags
        if (!reference.userTags) {
            this.selectedReferenceUserTags = reference.tags.slice(0);
        } else {
            this.selectedReferenceUserTags = reference.userTags.slice(0);
        }
    }
    hasTag(tags, tag) {
        return !!_.find(tags, e => e.data.pk == tag.data.pk);
    }
    @action.bound addTag(tag) {
        if (this.selectedReference && !_.find(this.workingTags, el => el.data.pk === tag.data.pk)) {
            this.workingTags.push(tag);
        }
    }
    @action.bound removeTag(tag) {
        _.remove(this.workingTags, el => el.data.pk === tag.data.pk);
    }
    @action.bound toggleTag(tag) {
        return this.hasTag(this.workingTags, tag) ? this.removeTag(tag) : this.addTag(tag);
    }
    @action.bound saveAndNext() {
        const payload = {
                pk: this.selectedReference.data.pk,
                tags: this.workingTags.map(tag => tag.data.pk),
            },
            success = () => {
                const $el = $(this.saveIndicatorElement),
                    index = _.findIndex(
                        this.references,
                        ref => ref.data.pk === this.selectedReference.data.pk
                    );

                if ($el.length !== 1) {
                    throw "`this.saveIndicatorElement` not found.";
                }

                this.errorOnSave = false;
                $el.fadeIn().fadeOut({
                    complete: () => {
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
                    },
                });
            },
            failure = data => {
                console.error(data);
                this.errorOnSave = true;
            };

        $.post(`/lit/api/reference/${this.selectedReference.data.pk}/tag/`, payload, v =>
            v.status === "success" ? success() : failure()
        ).fail(failure);
    }
    @action.bound removeAllTags() {
        this.workingTags.length = 0;
    }
    @action.bound setSaveIndicatorElement(el) {
        this.saveIndicatorElement = el;
    }

    @action.bound sortReferences(sortBy) {
        this.references = sortReferences(this.references, sortBy);
    }

    @action.bound toggleSlideAway() {
        this.filterClass = this.filterClass == "" ? "slideAway" : "";
    }

    @action.bound setInstructionsModal(input) {
        this.showInstructionsModal = input;
    }
}

export default Store;
