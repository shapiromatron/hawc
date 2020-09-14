import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";

import ReferenceComponent from "./components/Reference";

class Reference {
    constructor(data, tagtree) {
        this.data = data;
        this.tags = data.tags.map(tagId => tagtree.dict[tagId]);
    }

    static sortCompare(a, b) {
        if (a.data.authors > b.data.authors) return 1;
        if (a.data.authors < b.data.authors) return -1;
        return 0;
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

    print_self(el, options) {
        // remove after used
        ReactDOM.render(<ReferenceComponent reference={this} {...options} />, el);
    }

    print_name_str() {
        let authors = this.data.authors_short || this.data.authors || Reference.NO_AUTHORS_TEXT,
            year = this.data.year || "";
        return `${authors} ${year}`;
    }
}

_.extend(Reference, {
    NO_AUTHORS_TEXT: "[No authors listed]",
});

export default Reference;
