import $ from "$";
import _ from "lodash";
import d3 from "d3";

import Observee from "utils/Observee";
import NestedTag from "./NestedTag";

class TagTree extends Observee {
    constructor(rootNode) {
        super();
        this.tags = new NestedTag(rootNode, 0, self);
        this.dict = this._build_dictionary();
        this.observers = [];
    }

    get_nested_list(options) {
        // builds a nested list
        var div = $("<div>");
        this.tags.forEach(function(v) {
            v.get_nested_list_item(div, "", options);
        });
        return div;
    }

    get_options() {
        var list = [];
        this.tags.forEach(function(v) {
            v.get_option_item(list);
        });
        return list;
    }

    _build_dictionary() {
        var dict = {};
        this.tags.forEach(function(v) {
            v._append_to_dict(dict);
        });
        return dict;
    }

    tree_changed() {
        this.dict = this._build_dictionary();
        this.notifyObservers("TagTree");
    }

    remove_child(tag) {
        this.tags.splice_object(tag);
    }

    add_references(references) {
        var nodeDict = this.dict,
            addRef = function(ref) {
                nodeDict[ref.tag_id].references.push(ref.reference_id);
            };

        _.map(nodeDict, d => (d.references = []));
        _.each(references, addRef);

        var getNestedChildren = function(tag) {
            let refs = [].concat(tag.references),
                nested = tag.children ? _.flattenDeep(tag.children.map(getNestedChildren)) : [],
                uniqs;

            refs.push.apply(refs, nested);
            uniqs = _.uniq(refs);
            tag.data.reference_count = uniqs.length;
            return uniqs;
        };

        // set reference_count on each node.
        this.tags.forEach(getNestedChildren);
        if (this.data) {
            this.data.reference_count = d3.sum(_.map(this.tags, d => d.data.reference_count));
        }
    }

    build_top_level_node(name) {
        //transform top-level of tagtree to resemble node for plotting
        this.children = this.tags;
        this.data = {name};
    }

    get_tag(pk) {
        return this.dict[pk] || null;
    }
}

export default TagTree;
