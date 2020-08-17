import {action, computed, observable} from "mobx";

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

    @action.bound changeSelectedTag(selectedTag) {
        this.selectedTag = selectedTag;
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
                    `/lit/api/tags/${this.selectedTag}/references/?format=xlsx`,
                    "Download references",
                ],
                [
                    `/lit/api/tags/${this.selectedTag}/references-table-builder/?format=xlsx`,
                    "Download references (table-builder format)",
                ],
            ];
            if (this.config.canEdit) {
                links.push([
                    `/lit/tag/${this.selectedTag}/tag/`,
                    "Edit references with this tag (but not descendants)",
                ]);
            }
            return links;
        }
    }
}

export default Store;
