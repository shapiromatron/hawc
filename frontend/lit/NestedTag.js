import $ from "$";

import Observee from "utils/Observee";

import Reference from "./Reference";

class NestedTag extends Observee {
    constructor(item, depth, tree, parent, assessment_id, search_id) {
        super();
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

    get_reference_objects_by_tag(reference_viewer, options) {
        options = options || {filteredSubset: false};
        let url = `/lit/assessment/${this.assessment_id}/references/${this.data.pk}/json/`;
        if (this.search_id) {
            url += `?search_id=${this.search_id}`;
        }

        $.get(url, results => {
            if (results.status == "success") {
                let refs = results.refs.map(datum => new Reference(datum, this.tree));
                if (options.filteredSubset) {
                    let expected_references = new Set(this.get_references_deep());
                    refs = refs.filter(ref => expected_references.has(ref.data.pk));
                }
                reference_viewer.set_references(refs);
            } else {
                reference_viewer.set_error();
            }
        });
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

    add_child(name) {
        var data = {
            status: "add",
            parent_pk: this.data.pk,
            name,
        };

        $.post(".", data, v => {
            if (v.status === "success") {
                this.children.push(
                    new NestedTag(
                        v.node[0],
                        this.depth + 1,
                        this.tree,
                        this,
                        this.assessment_id,
                        this.search_id
                    )
                );
                this.tree.tree_changed();
            }
        });
    }

    remove_self() {
        this.children.forEach(function(v) {
            v.remove_self();
        });
        var self = this,
            data = {
                status: "remove",
                pk: this.data.pk,
            };

        $.post(".", data, function(v) {
            if (v.status === "success") {
                self.notifyObservers({event: "tag removed", object: self});
                if (self.parent) {
                    self.parent.remove_child(self);
                } else {
                    self.tree.remove_child(self);
                }
                self.tree.tree_changed();
            }
        });
    }

    move_self(offset) {
        var self = this,
            lst = this.parent.children,
            index = lst.indexOf(this),
            data = {
                status: "move",
                pk: this.data.pk,
                offset,
            };

        // update locally
        lst.splice(index + offset, 0, lst.splice(index, 1)[0]);

        $.post(".", data, function(v) {
            if (v.status === "success") self.tree.tree_changed();
        });
    }

    rename_self(name) {
        var self = this,
            data = {
                status: "rename",
                pk: this.data.pk,
                name,
            };

        $.post(".", data, function(v) {
            if (v.status === "success") {
                self.data.name = name;
                self.tree.tree_changed();
            }
        });
    }

    remove_child(tag) {
        this.children.splice_object(tag);
    }
}

export default NestedTag;
