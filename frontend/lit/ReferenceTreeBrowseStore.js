import $ from "$";
import {action, computed, observable} from "mobx";

import Reference from "./Reference";
import TagTree from "./TagTree";

class Store {
    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id);
        this.tagtree.add_references(config.references);
    }

    @observable selectedTag = null;
    @observable config = null;
    @observable tagtree = null;
    @observable selectedReferences = null;
    @observable selectedReferencesLoading = false;

    @action.bound changeSelectedTag(selectedTag) {
        this.selectedTag = selectedTag;
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
            // CHECK THIS PART
            url += `?search_id=${this.search_id}`;
        }
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = results.refs.map(datum => new Reference(datum, this.tagtree));
            this.selectedReferencesLoading = false;
        });
    }
    @action.bound viewUntaggedReferences() {
        console.warning("viewUntaggedReferences");
    }

    @computed get getActionLinks() {
        let links = [];
        if (this.selectedTag === null) {
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
