import _ from "lodash";

class Reference {
    constructor(data, tagtree) {
        this.data = data;
        this.tags = data.tags.map(tagId => tagtree.dict[tagId]);
    }

    static get_detail_url(id, subtype) {
        switch (subtype) {
            case "hero":
                return `https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/${id}`;
            case "pubmed":
                return `https://pubmed.ncbi.nlm.nih.gov/${id}/`;
            case "reference":
            default:
                return `/lit/reference/${id}/`;
        }
    }

    get_edit_url() {
        return `/lit/reference/${this.data.pk}/edit/`;
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
