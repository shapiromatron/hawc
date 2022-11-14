import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import $ from "$";

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
    @observable errorOnSave = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.array(config.refs, this.tagtree);
        // set first reference
        if (this.referencesUntagged.length > 0) {
            this.changeSelectedReference(this.referencesUntagged[0]);
        } else if (this.references.length === 1) {
            this.changeSelectedReference(this.references[0]);
        }
    }

    @action.bound changeSelectedReference(reference) {
        this.selectedReference = reference;
        this.selectedReferenceTags = reference.tags.slice(0); // shallow copy
    }
    @action.bound addTag(tag) {
        if (
            this.selectedReference &&
            !_.find(this.selectedReferenceTags, el => el.data.pk === tag.data.pk)
        ) {
            this.selectedReferenceTags.push(tag);
        }
    }
    @action.bound removeTag(tag) {
        _.remove(this.selectedReferenceTags, el => el.data.pk === tag.data.pk);
    }
    @action.bound saveAndNext() {
        const payload = {
                pk: this.selectedReference.data.pk,
                tags: this.selectedReferenceTags.map(tag => tag.data.pk),
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
                        this.references.splice(index, 1, toJS(this.selectedReference));
                        this.selectedReference = null;
                        this.selectedReferenceTags = null;
                        if (this.referencesUntagged.length > 0) {
                            this.changeSelectedReference(this.referencesUntagged[0]);
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
        this.selectedReferenceTags = [];
    }
    @action.bound setSaveIndicatorElement(el) {
        this.saveIndicatorElement = el;
    }

    @action.bound sortReferences(sortBy) {
        this.references = sortReferences(this.references, sortBy);
    }

    @computed get referencesTagged() {
        return this.references.filter(ref => ref.tags.length > 0);
    }
    @computed get referencesUntagged() {
        return this.references.filter(ref => ref.tags.length === 0);
    }
}

export default Store;
