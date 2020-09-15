import $ from "$";
import {action, computed, observable} from "mobx";

import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id);
        this.tagtree.add_references(config.references);
    }

    selectedTagNode = null;
    @observable untaggedReferencesSelected = false;
    @observable selectedTag = null;
    @observable config = null;
    @observable tagtree = null;
    @observable selectedReferences = null;
    @observable selectedReferencesLoading = false;

    @action.bound changeSelectedTagNodeClass(targetNode) {
        if (this.selectedTagNode) {
            $(this.selectedTagNode).removeClass("selected");
        }
        this.selectedTagNode = targetNode;
        $(this.selectedTagNode).addClass("selected");
    }
    @action.bound handleTagClick(selectedTag) {
        this.changeSelectedTagNodeClass(event.target);
        this.selectedTag = selectedTag;
        this.untaggedReferencesSelected = false;
        this.requestSelectedReferences();
    }
    @action.bound requestSelectedReferences() {
        this.selectedReferences = null;
        this.selectedReferencesLoading = false;
        if (this.selectedTag === null) {
            return;
        }

        let url = `/lit/assessment/${this.config.assessment_id}/references/${this.selectedTag.data.pk}/json/`;
        if (this.config.search_id) {
            url += `?search_id=${this.config.search_id}`;
        }
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = results.refs.map(datum => new Reference(datum, this.tagtree));
            this.selectedReferencesLoading = false;
        });
    }
    @action.bound handleUntaggedReferenceClick() {
        this.changeSelectedTagNodeClass(event.target);

        const {assessment_id, search_id} = this.config;

        let url = `/lit/assessment/${assessment_id}/references/untagged/json/`;
        if (search_id) {
            url += `?search_id=${search_id}`;
        }

        this.selectedTag = null;
        this.untaggedReferencesSelected = true;
        this.selectedReferences = null;
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = results.refs.map(datum => new Reference(datum, this.tagtree));
            this.selectedReferencesLoading = false;
        });
    }

    @computed get getActionLinks() {
        let links = [];
        if (this.selectedTag === null || this.untaggedReferencesSelected === true) {
            return links;
        } else {
            links = [
                [
                    `/lit/api/tags/${this.selectedTag.data.pk}/references/?format=xlsx`,
                    "Download references",
                ],
                [
                    `/lit/api/tags/${this.selectedTag.data.pk}/references-table-builder/?format=xlsx`,
                    "Download references (table-builder format)",
                ],
            ];
            if (this.config.canEdit) {
                links.push([
                    `/lit/tag/${this.selectedTag.data.pk}/tag/`,
                    "Edit references with this tag (but not descendants)",
                ]);
            }
            return links;
        }
    }
}

export default Store;
