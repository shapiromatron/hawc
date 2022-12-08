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
    @observable reference = null;
    @observable referenceTags = null;
    @observable referenceUserTags = null;
    @observable errorOnSave = false;
    @observable filterClass = "";
    @observable showInstructionsModal = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.references = Reference.array(config.refs, this.tagtree);
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
            success = () => {
                const $el = $(this.saveIndicatorElement),
                    index = _.findIndex(
                        this.references,
                        ref => ref.data.pk === this.reference.data.pk
                    );

                if ($el.length !== 1) {
                    throw "`this.saveIndicatorElement` not found.";
                }

                this.errorOnSave = false;
                $el.fadeIn().fadeOut({
                    complete: () => {
                        this.reference.userTags = toJS(this.referenceUserTags);
                        if (!this.config.conflict_resolution) {
                            this.reference.tags = toJS(this.referenceUserTags);
                        }
                        const nextIndex = this.references.length > index + 1 ? index + 1 : 0,
                            reference = this.references[nextIndex];
                        this.setReference(reference);
                    },
                });
            },
            failure = data => {
                console.error(data);
                this.errorOnSave = true;
            };
        $.post(url, payload, v => (v.status === "success" ? success() : failure())).fail(failure);
    }
    @action.bound removeAllTags() {
        this.referenceUserTags = [];
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
