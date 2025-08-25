import React from "react";
import ReactDOM from "react-dom";
import {createRoot} from "react-dom/client";

import NestedTag from "./NestedTag";
import TagTreeComponent from "./components/TagTree";

class TagTree {
    constructor(rootNode, assessment_id, search_id) {
        this.assessment_id = assessment_id;
        this.search_id = search_id;
        this.rootNode = new NestedTag(rootNode, 0, this, null, assessment_id, search_id);
        // build dictionary
        this.dict = {};
        this.rootNode._append_to_dict(this.dict);
    }

    getById(tagId) {
        return this.dict[tagId];
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

    render(el, options) {
        const root = createRoot(el);
        root.render(<TagTreeComponent tagtree={this} {...options} />);
    }

    choices() {
        // get choices for a select input
        const choices = [],
            addTag = function (tag) {
                choices.push({id: tag.data.pk, label: tag.get_full_name()});
                tag.children.forEach(addTag);
            };
        this.rootNode.children.forEach(addTag);
        return choices;
    }
}

export default TagTree;
