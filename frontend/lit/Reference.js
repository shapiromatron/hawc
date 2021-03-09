import _ from "lodash";

import HAWCUtils from "utils/HAWCUtils";

class Reference {
    constructor(data, tagtree) {
        this.data = data;
        this._quickSearchText = `${data.title}-${data.year}-${data.authors}-${data.authors_short}`.toLowerCase();
        this.tags = data.tags.map(tagId => tagtree.dict[tagId]);
    }

    static get_detail_url(id, subtype) {
        switch (subtype) {
            case "hero":
                return HAWCUtils.getHeroUrl(id);
            case "pubmed":
                return `https://pubmed.ncbi.nlm.nih.gov/${id}/`;
            case "reference":
            default:
                return `/lit/reference/${id}/`;
        }
    }

    static sorted(references) {
        return _.chain(references)
            .sortBy(d => d.data.year)
            .reverse()
            .value();
    }

    get_edit_url() {
        return `/lit/reference/${this.data.pk}/edit/`;
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
