import $ from "$";
import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";

import Observee from "utils/Observee";
import ReferenceComponent from "./components/Reference";

class Reference extends Observee {
    constructor(data, tagtree) {
        super();
        var self = this,
            tag_ids = data.tags;
        this.data = data;
        this.data.tags = [];
        tag_ids.forEach(function(v) {
            self.add_tag(tagtree.dict[v]);
        });
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

    print_edit_taglist() {
        return this.data.tags.map(d =>
            $(
                `<span title="click to remove" class="refTag refTagEditing">${d.get_full_name()}</span>`
            ).data("d", d)
        );
    }

    print_name_str() {
        let authors = this.data.authors_short || this.data.authors || Reference.NO_AUTHORS_TEXT,
            year = this.data.year || "";
        return `${authors} ${year}`;
    }

    print_name() {
        this.$list = $(`<p class="reference">${this.print_name_str()}</p>`).data("d", this);
        return this.$list;
    }

    select_name() {
        this.$list.addClass("selected");
    }

    deselect_name() {
        this.$list.removeClass("selected");
    }

    add_tag(tag) {
        var tag_already_exists = false;
        this.data.tags.forEach(function(v) {
            if (tag === v) {
                tag_already_exists = true;
            }
        });
        if (tag_already_exists) return;
        this.data.tags.push(tag);
        tag.addObserver(this);
        this.notifyObservers();
    }

    remove_tag(tag) {
        this.data.tags.splice_object(tag);
        tag.removeObserver(this);
        this.notifyObservers();
    }

    remove_tags() {
        this.data.tags = [];
        this.notifyObservers();
    }

    save(success, failure) {
        var data = {
            pk: this.data.pk,
            tags: this.data.tags.map(function(v) {
                return v.data.pk;
            }),
        };
        $.post(".", data, function(v) {
            return v.status === "success" ? success() : failure();
        }).fail(failure);
    }

    update(status) {
        if (status.event == "tag removed") {
            this.remove_tag(status.object);
        }
    }
}

_.extend(Reference, {
    NO_AUTHORS_TEXT: "[No authors listed]",
});

export default Reference;
