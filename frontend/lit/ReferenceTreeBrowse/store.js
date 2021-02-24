import $ from "$";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id);
        this.tagtree.add_references(config.references);
    }

    @observable untaggedReferencesSelected = false;
    @observable selectedTag = null;
    @observable config = null;
    @observable tagtree = null;
    @observable selectedReferences = null;
    @observable yearFilter = null;
    @observable selectedReferencesLoading = false;

    @action.bound handleTagClick(selectedTag) {
        h.pushUrlParamsState("tag_id", selectedTag.data.pk);
        this.selectedTag = selectedTag;
        this.untaggedReferencesSelected = false;
        this.requestSelectedReferences();
    }
    @action.bound requestSelectedReferences() {
        this.yearFilter = null;
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
            const references = Reference.sorted(
                results.refs.map(datum => new Reference(datum, this.tagtree))
            );
            this.yearFilter = null;
            this.selectedReferences = references;
            this.selectedReferencesLoading = false;
        });
    }
    @action.bound handleUntaggedReferenceClick() {
        const {assessment_id, search_id} = this.config;

        let url = `/lit/assessment/${assessment_id}/references/untagged/json/`;
        if (search_id) {
            url += `?search_id=${search_id}`;
        }

        h.pushUrlParamsState("tag_id", null);
        this.selectedTag = null;
        this.untaggedReferencesSelected = true;
        this.selectedReferences = null;
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = results.refs.map(datum => new Reference(datum, this.tagtree));
            this.selectedReferencesLoading = false;
        });
    }
    @action.bound tryLoadTag() {
        // if `tag_id` is set in the URL query string, try to load this tag ID.
        const params = new URLSearchParams(location.search),
            tagId = parseInt(params.get("tag_id")),
            nestedTag = this.tagtree.getById(tagId);

        if (nestedTag) {
            this.handleTagClick(nestedTag);
        }
    }
    @action.bound updateYearFilter(filter) {
        this.yearFilter = filter;
    }

    @computed get filteredReferences() {
        const filter = this.yearFilter;
        if (!filter) {
            return this.selectedReferences;
        }
        return this.selectedReferences.filter(
            d => d.data.year >= filter.min && d.data.year <= filter.max
        );
    }

    @computed get getActionLinks() {
        let links = [];
        if (this.untaggedReferencesSelected === true && this.config.canEdit) {
            links.push([
                `/lit/assessment/${this.config.assessment_id}/tag/untagged/`,
                "Tag untagged references",
            ]);
        } else if (this.selectedTag !== null) {
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
                    "Tag references with this tag (but not descendants)",
                ]);
            }
        }
        return links;
    }
}

export default Store;
