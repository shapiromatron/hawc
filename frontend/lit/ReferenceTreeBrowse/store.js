import {action, autorun, computed, observable} from "mobx";
import h from "shared/utils/helpers";
import $ from "$";

import Reference from "../Reference";
import TagTree from "../TagTree";
import {sortReferences} from "../constants";

class Store {
    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id);
        this.tagtree.add_references(config.references);
        // pagination should be reset when the filters change
        // to ensure that the current page is not out of bounds
        autorun(() => (this.currentPage = this.filteredReferences ? 1 : null));
    }

    paginateBy = 50;

    @observable untaggedReferencesSelected = false;
    @observable selectedTag = null;
    @observable config = null;
    @observable tagtree = null;
    @observable selectedReferences = null;
    @observable selectedReferencesLoading = false;
    @observable currentPage = null;

    @computed get page() {
        if (!this.selectedReferences) {
            return null;
        }

        let {currentPage, filteredReferences} = this,
            totalPages = Math.ceil(filteredReferences.length / this.paginateBy);

        return {
            currentPage,
            totalPages,
            next: currentPage < totalPages ? currentPage + 1 : null,
            previous: currentPage > 1 ? currentPage - 1 : null,
        };
    }

    @action.bound fetchPage(page) {
        this.currentPage = page;
    }

    @computed get paginatedReferences() {
        if (!this.selectedReferences) {
            return null;
        }

        let refs = this.filteredReferences,
            start = (this.currentPage - 1) * this.paginateBy,
            end = this.currentPage * this.paginateBy;

        return refs.slice(start, end);
    }

    @action.bound handleTagClick(selectedTag) {
        h.pushUrlParamsState("tag_id", selectedTag.data.pk);
        this.selectedTag = selectedTag;
        this.untaggedReferencesSelected = false;
        this.requestSelectedReferences();
    }
    @action.bound requestSelectedReferences() {
        this.selectedReferences = null;
        this.selectedReferencesLoading = false;
        this.resetFilters();
        if (this.selectedTag === null) {
            return;
        }

        let url = `/lit/api/assessment/${this.config.assessment_id}/references/?all&tag_id=${this.selectedTag.data.pk}`;
        if (this.config.search_id) {
            url += `&search_id=${this.config.search_id}`;
        }
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = Reference.array(results, this.tagtree);
            this.selectedReferencesLoading = false;
        });
    }
    @action.bound handleUntaggedReferenceClick() {
        const {assessment_id, search_id} = this.config;

        let url = `/lit/api/assessment/${assessment_id}/references/?all=1&untagged=1`;
        if (search_id) {
            url += `&search_id=${search_id}`;
        }

        h.pushUrlParamsState("tag_id", null);
        this.selectedTag = null;
        this.untaggedReferencesSelected = true;
        this.selectedReferences = null;
        this.selectedReferencesLoading = true;
        $.get(url, results => {
            this.selectedReferences = Reference.array(results, this.tagtree);
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

    @computed get filteredReferences() {
        const filter = this.yearFilter,
            quickFilterText = this.quickFilterText;
        let refs = this.selectedReferences;

        if (!refs) {
            return refs;
        }

        if (quickFilterText) {
            refs = refs.filter(d => d._quickSearchText.includes(quickFilterText));
        }
        if (filter) {
            refs = refs.filter(d => d.data.year >= filter.min && d.data.year <= filter.max);
        }
        return refs;
    }

    @action.bound sortReferences(sortBy) {
        this.selectedReferences = sortReferences(this.selectedReferences, sortBy);
    }

    // year filter
    @observable yearFilter = null;
    @action.bound updateYearFilter(filter) {
        this.yearFilter = filter;
    }

    // quick search
    @observable quickFilterText = "";
    @action.bound changeQuickFilterText(text) {
        this.quickFilterText = text.trim().toLowerCase();
    }

    @action.bound resetFilters() {
        this.yearFilter = null;
        this.quickFilterText = "";
    }

    // used in ReferenceTableMain
    @observable activeReferenceTableTab = 0;
    @action.bound changeActiveReferenceTableTab(index) {
        this.activeReferenceTableTab = index;
        return true;
    }
}

export default Store;
