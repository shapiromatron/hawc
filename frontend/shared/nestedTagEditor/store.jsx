import _ from "lodash";
import {action, makeObservable, observable} from "mobx";
import h from "shared/utils/helpers";

import {NO_PARENT} from "./constants";

class TagEditorStore {
    @observable tagsLoaded = false;
    @observable tags = [];
    @observable parentOptions = [];
    @observable tagCounts = false;

    constructor(config) {
        makeObservable(this);
        this.config = config;
        this.tagReferences =
            "references" in config
                ? _.mapValues(_.groupBy(config.references, "tag_id"), refs =>
                      refs.map(ref => ref.reference_id)
                  )
                : false;
    }

    @action.bound fetchTags() {
        const url = this.config.list_url,
            getOptions = function (nodes) {
                let opts = [],
                    addOption = function (node) {
                        let indentedName =
                            _.times(node.data.depth, _d => "━ ").join("") + node.data.name;
                        opts.push([node.id, indentedName]);
                        if (node.children) {
                            node.children.forEach(addOption);
                        }
                    };

                nodes.forEach(addOption);
                opts.unshift([NO_PARENT, "---"]);
                return opts;
            },
            addNodeDepth = function (node, depth) {
                // add depth to each node, and recursively to child nodes
                node.data.depth = depth;
                if (node.children) {
                    node.children.forEach(d => addNodeDepth(d, depth + 1));
                }
            },
            addNodeReferenceCount = function (node, tagReferences) {
                // add references to each node, and recursively to child nodes
                node.data.references = new Set(tagReferences[node.id]);
                if (node.children) {
                    node.children.forEach(
                        d =>
                            (node.data.references = node.data.references.union(
                                addNodeReferenceCount(d, tagReferences)
                            ))
                    );
                }
                node.data.tagCount = node.data.references.size;
                return node.data.references;
            };
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(allTags => {
                let tags = allTags[0].children || [];
                tags.forEach(d => addNodeDepth(d, 0));
                if (this.tagReferences) {
                    tags.forEach(d => addNodeReferenceCount(d, this.tagReferences));
                }
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
            .then(_json => this.fetchTags())
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
            .then(_json => this.fetchTags())
            .catch(ex => console.error("Tag patch failed", ex));
    }
}

export default TagEditorStore;
