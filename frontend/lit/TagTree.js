import $ from "$";
import _ from "lodash";
import d3 from "d3";

import Observee from "utils/Observee";

import NestedTag from "./NestedTag";
import Reference from "./Reference";

class TagTree extends Observee {
    constructor(data) {
        super();
        this.tags = this._construct_tags(data[0], true);
        this.dict = this._build_dictionary();
        this.observers = [];
    }

    add_root_tag(name) {
        var self = this,
            data = {
                content: "tag",
                status: "add",
                name,
            };
        $.post(".", data, function(v) {
            if (v.status === "success") {
                self.tags.push(new NestedTag(v.node[0], 0, self));
                self.tree_changed();
            }
        });
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

    _construct_tags(data, skip_root) {
        // unpack our tags and construct NestedTag objects
        var self = this,
            tags = [];
        if (skip_root) {
            if (data.children) {
                data.children.forEach(function(v) {
                    tags.push(new NestedTag(v, 0, self));
                });
            }
        } else {
            tags.push(new NestedTag(data, 0, self));
        }
        return tags;
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
                nodeDict[ref.tag_id].references.push(ref.content_object_id);
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

    view_untagged_references(reference_viewer) {
        var url = "/lit/assessment/{0}/references/untagged/json/".printf(window.assessment_pk);
        if (window.search_id) url += "?search_id={0}".printf(window.search_id);

        $.get(url, function(results) {
            if (results.status == "success") {
                var refs = [];
                results.refs.forEach(function(datum) {
                    refs.push(new Reference(datum, window.tagtree));
                });
                reference_viewer.set_references(refs);
            } else {
                reference_viewer.set_error();
            }
        });
    }

    get_tag(pk) {
        return this.dict[pk] || null;
    }
}

export default TagTree;
