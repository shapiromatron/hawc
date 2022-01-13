import $ from "$";
import ReactDOM from "react-dom";
import React from "react";

import Loading from "shared/components/Loading";
import Alert from "shared/components/Alert";
import ReferenceTable from "lit/components/ReferenceTable";
import Reference from "./Reference";
import PaginatedReferenceList from "./components/PaginatedReferenceList";

class NestedTag {
    constructor(item, depth, tree, parent, assessment_id, search_id) {
        this.observers = [];
        this.references = new Set();
        this.parent = parent;
        this.data = item.data;
        this.data.pk = item.id;
        this.depth = depth;
        this.tree = tree;
        this.assessment_id = assessment_id;
        this.search_id = search_id;

        let children;
        if (item.children) {
            children = item.children.map(
                v => new NestedTag(v, depth + 1, tree, this, this.assessment_id, this.search_id)
            );
        } else {
            children = [];
        }
        this.children = children;
        return this;
    }

    get_references_deep() {
        let set = new Set([...this.references.values()]);
        this.children.forEach(child => {
            [...child.get_references_deep()].forEach(set.add, set);
        });
        return [...set.values()];
    }

    _append_to_dict(dict) {
        dict[this.data.pk] = this;
        this.children.forEach(child => child._append_to_dict(dict));
    }

    get_full_name() {
        // omit root-tag name
        let parentName = this.parent.depth > 0 ? this.parent.get_full_name() : null;
        if (parentName) {
            return `${parentName} ➤ ${this.data.name}`;
        } else {
            return this.data.name;
        }
    }

    renderPaginatedReferenceList(el, canEdit) {
        const settings = {
            assessment_id: this.assessment_id,
            tag_id: this.data.pk,
            search_id: this.search_id,
            tag: this,
        };
        ReactDOM.render(<PaginatedReferenceList settings={settings} canEdit={canEdit} />, el);
    }

    renderReferenceList(el) {
        let url = `/lit/assessment/${this.assessment_id}/references/${this.data.pk}/json/`;
        if (this.search_id) {
            url += `?search_id=${this.search_id}`;
        }
        ReactDOM.render(<Loading />, el);

        $.get(url, results => {
            if (results.status == "success") {
                let expected_references = new Set(this.get_references_deep()),
                    refs = Reference.sortedArray(results.refs, this.tree).filter(ref =>
                        expected_references.has(ref.data.pk)
                    );

                ReactDOM.render(<ReferenceTable references={refs} showActions={false} />, el);
            } else {
                ReactDOM.render(<Alert />, el);
            }
        });
    }
}

export default NestedTag;
