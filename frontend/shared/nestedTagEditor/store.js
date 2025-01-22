import _ from "lodash";
import {action, observable} from "mobx";
import h from "shared/utils/helpers";

import {NO_PARENT} from "./constants";

class TagEditorStore {
    @observable tagsLoaded = false;
    @observable tags = [];
    @observable parentOptions = [];

    constructor(config) {
        this.config = config;
        this.tagCounts = false;
        this.tagCounts =
            "references" in this.config ? _.countBy(this.config.references, "tag_id") : false;
    }

    @action.bound fetchTags() {
        const url = this.config.list_url,
            getOptions = function(nodes) {
                let opts = [],
                    addOption = function(node) {
                        let indentedName =
                            _.times(node.data.depth, d => "━ ").join("") + node.data.name;
                        opts.push([node.id, indentedName]);
                        if (node.children) {
                            node.children.forEach(addOption);
                        }
                    };

                nodes.forEach(addOption);
                opts.unshift([NO_PARENT, "---"]);
                return opts;
            },
            addDepthAndCount = function(node, depth, tagCounts) {
                // add depth to each node, and recursively to child nodes
                node.data.depth = depth;
                node.data.tagCount = tagCounts ? tagCounts[node.id] : false;

                if (node.children) {
                    node.children.forEach(d => addDepthAndCount(d, depth + 1, tagCounts));
                }
            };

        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(allTags => {
                let tags = allTags[0].children || [];
                tags.forEach(d => addDepthAndCount(d, 0, this.tagCounts));

                this.tags = tags;
                this.parentOptions = getOptions(tags);
                this.tagsLoaded = true;
            })
            .catch(ex => console.error("Tag parsing failed", ex));
    }

    @action.bound createTag(newNode) {
        const {base_url, assessment_id, csrf} = this.config,
            url = `${base_url}?assessment_id=${assessment_id}`,
            obj = {
                assessment_id,
                name: newNode.name,
                parent: newNode.parent,
            };

        return fetch(url, h.fetchPost(csrf, obj, "POST"))
            .then(response => {
                if (response.ok) {
                    this.fetchTags();
                }
            })
            .catch(ex => console.error("Tag patch failed", ex));
    }

    @action.bound updateTag(id, newNode) {
        const url = `${this.config.base_url}${id}/`,
            csrf = this.config.csrf,
            obj = {
                name: newNode.name,
                parent: newNode.parent,
            };

        return fetch(url, h.fetchPost(csrf, obj, "PATCH"))
            .then(response => response.json())
            .then(json => this.fetchTags())
            .catch(ex => console.error("Tag patch failed", ex));
    }

    @action.bound deleteTag(id) {
        const url = `${this.config.base_url}${id}/`,
            csrf = this.config.csrf;

        return fetch(url, h.fetchDelete(csrf))
            .then(response => {
                if (response.ok) {
                    return this.fetchTags();
                }
            })
            .catch(ex => console.error("Tag delete failed", ex));
    }

    @action.bound moveTag(nodeId, oldIndex, newIndex) {
        const url = `${this.config.base_url}${nodeId}/move/`,
            csrf = this.config.csrf,
            obj = {
                oldIndex,
                newIndex,
            };

        return fetch(url, h.fetchPost(csrf, obj, "PATCH"))
            .then(response => response.json())
            .then(json => this.fetchTags())
            .catch(ex => console.error("Tag patch failed", ex));
    }
}

export default TagEditorStore;
