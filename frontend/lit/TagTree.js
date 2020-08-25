import $ from "$";

import Observee from "utils/Observee";
import NestedTag from "./NestedTag";

class TagTree extends Observee {
    constructor(rootNode, assessment_id, search_id) {
        super();
        this.assessment_id = assessment_id;
        this.search_id = search_id;
        this.rootNode = new NestedTag(rootNode, 0, this, null, assessment_id, search_id);
        this.dict = this._build_dictionary();
        this.observers = [];
    }

    get_nested_list(options) {
        // builds a nested list
        let div = $("<div>");
        this.rootNode.children.forEach(child => child.get_nested_list_item(div, "", options));
        return div;
    }

    get_options() {
        let list = [];
        this.rootNode.get_option_item(list);
        return list;
    }

    _build_dictionary() {
        let dict = {};
        this.rootNode._append_to_dict(dict);
        return dict;
    }

    tree_changed() {
        this.dict = this._build_dictionary();
        this.notifyObservers("TagTree");
    }

    add_references(references) {
        references.forEach(el => {
            let node = this.dict[el.tag_id];
            if (node) {
                node.references.add(el.reference_id);
            } else {
                console.error(`Tag not found ${el.tag_id}; reference id: ${el.reference_id}`);
            }
        });
    }

    rename_top_level_node(name) {
        this.rootNode.data.name = name;
    }

    get_tag(pk) {
        return this.dict[pk] || null;
    }

    prune_tree(pk) {
        // Remove a NestedTag from a parent tree. The dictionary still contains this
        // node, but it will not be accessed by crawling the tree.
        let tag = this.dict[pk],
            index = tag.parent.children.findIndex(el => el === tag);
        tag.parent.children.splice(index, 1);
    }

    prune_no_references(hideEmpty) {
        // Severs leaves and subtrees where nodes have no references,
        // starting with the children of root node;
        // Effectively removes no-reference nodes from tree starting at root
        const _prune = node => {
            /*
            Recursively show/hide references if no nodes are available.
            Returns true if the node should be pruned, false to keep
            */

            // make a copy of original tree, if exists
            if (node._children === undefined) {
                node._children = node.children;
            }

            // recurse children before returning this one
            const valid_children = [];
            for (const child of node._children) {
                if (!_prune(child)) {
                    valid_children.push(child);
                }
            }
            node.children = valid_children;

            if (hideEmpty) {
                return node.get_references_deep().length == 0;
            }
            return false;
        };
        _prune(this.rootNode);
    }

    reset_root_node(pk) {
        // Change the root node for this tagtree; useful for displaying a subset of the tree
        let tag = this.dict[pk];
        if (tag.data.pk !== this.rootNode.data.pk) {
            this.rootNode = tag;
        }
    }
}

export default TagTree;
