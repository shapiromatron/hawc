import _ from "lodash";
import Hero from "shared/utils/Hero";

import {sortReferences} from "./constants";

class Reference {
    constructor(data, tagtree) {
        this.data = data;
        this._quickSearchText = `${data.title}-${data.year}-${data.authors}-${data.authors_short}`.toLowerCase();
        this.tags = data.tags.map(tagId => tagtree.dict[tagId]);
        this.userTags = data.user_tags ? data.user_tags.map(tagId => tagtree.dict[tagId]) : null;
    }

    static get_detail_url(id, subtype) {
        switch (subtype) {
            case "hero":
                return Hero.getUrl(id);
            case "pubmed":
                return `https://pubmed.ncbi.nlm.nih.gov/${id}/`;
            case "reference":
            default:
                return `/lit/reference/${id}/`;
        }
    }

    static array(data, tagtree, sort = true) {
        const refs = _.map(data, d => new Reference(d, tagtree));
        return sort ? sortReferences(refs) : refs;
    }

    get_edit_url() {
        return `/lit/reference/${this.data.pk}/update/`;
    }

    get_study_url() {
        if (this.data.has_study) {
            return `/study/${this.data.pk}/`;
        }
        return null;
    }

    shortCitation() {
        let authors = this.data.authors_short || this.data.authors || Reference.NO_AUTHORS_TEXT,
            year = this.data.year || "";
        return `${authors} ${year}`;
    }
}

_.extend(Reference, {
    NO_AUTHORS_TEXT: "[No authors listed]",
});

export default Reference;
