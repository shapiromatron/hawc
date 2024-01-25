import {action, autorun, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

import $ from "$";

import {sortReferences} from "../constants";
import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0], config.assessment_id, config.search_id);
        this.tagtree.add_references(config.references);
        autorun(() => (this.current_page = this.filteredReferences ? 1 : null));
    }

    pagination = 25;

    @observable untaggedReferencesSelected = false;
    @observable selectedTag = null;
    @observable config = null;
    @observable tagtree = null;
    @observable selectedReferences = null;
    @observable selectedReferencesLoading = false;
    @observable current_page = null;

    @computed get page() {
        if (!this.current_page) {
            return null;
        }

        let refs = toJS(this.filteredReferences),
            {current_page} = this,
            total_pages = Math.ceil(refs.length / this.pagination);

        return {
            current_page,
            total_pages,
            next: current_page < total_pages ? current_page + 1 : null,
            previous: current_page > 1 ? current_page - 1 : null,
        };
    }

    @action.bound fetchPage(page) {
        this.current_page = page;
    }

    @computed get paginatedReferences() {
        let refs = toJS(this.filteredReferences);

        if (!this.current_page) {
            return refs;
        }

        let start = (this.current_page - 1) * this.pagination,
            end = this.current_page * this.pagination;

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
