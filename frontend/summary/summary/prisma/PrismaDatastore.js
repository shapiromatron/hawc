import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

class PrismaDatastore {
    constructor(settings, dataset, options) {
        this.settings = settings;
        this.dataset = dataset;
        this.options = options;
        this.createMaps();
        this.updateTagMap();
        this.sections = this.getDiagramSections();
        this.setRefs();
        this.settingsHash = h.hashString(JSON.stringify(this.settings));
        this.modal = new HAWCModal();
    }

    getDiagramSections() {
        const {sections, boxes} = this.settings;
        return sections
            .filter(section => section.label.length > 0)
            .map(section => {
                return {
                    label: section.label,
                    key: section.key,
                    blocks: boxes
                        .filter(b => b.section === section.key)
                        .map(b => {
                            return {
                                label: b.label,
                                key: b.key,
                                tags: b.tag,
                                count_strategy: b.count_strategy,
                                box_layout: b.box_layout,
                                items: b.items,
                            };
                        }),
                };
            });
    }

    getConnections() {
        return this.settings.arrows;
    }

    createMaps() {
        this.maps = {};

        // for each reference-tag pair we are adding the reference id
        // to the set associated with the tag id in our tag map
        this.maps.tagMap = this.dataset.reference_tag_pairs.reduce(
            (map, pair) =>
                map.set(
                    pair.tag_id,
                    map.has(pair.tag_id)
                        ? map.get(pair.tag_id).add(pair.reference_id)
                        : new Set([pair.reference_id])
                ),
            new Map()
        );
        // for each reference-search pair we are adding the reference id
        // to the set associated with the search id in our search map
        this.maps.searchMap = this.dataset.reference_search_pairs.reduce(
            (map, pair) =>
                map.set(
                    pair.search_id,
                    map.has(pair.search_id)
                        ? map.get(pair.search_id).add(pair.reference_id)
                        : new Set([pair.reference_id])
                ),
            new Map()
        );
    }

    updateTagMap() {
        let index = 0,
            recursivelyUpdate = () => {
                // this function recursively updates the map by
                // going to leaf nodes and working its way back.
                let tag = this.dataset.tags[index++],
                    nextTag = this.dataset.tags[index];
                // while the next tag is a child of current tag...
                while (nextTag && nextTag.depth == tag.depth + 1) {
                    // update the child map through recursion
                    recursivelyUpdate();
                    // add the updated child map to the parent map
                    this.maps.tagMap.set(
                        tag.id,
                        (this.maps.tagMap.get(tag.id) || new Set()).union(
                            this.maps.tagMap.get(nextTag.id) || new Set()
                        )
                    );
                    // move on to the next child candidate
                    nextTag = this.dataset.tags[index];
                }
            };
        while (index < this.dataset.tags.length) {
            // recursively update each subtree with root parent
            recursivelyUpdate();
        }
    }

    tag_lookup(tag) {
        // the "tag" identifiers have the form "{type}_{id}",
        // where "type" can be tag or search
        // this function splits the identifier and uses the metadata
        // to retrieve the set of reference ids associated with it
        // from the relevant map
        let [type, id] = tag.split("_");
        if (type == "tag") {
            // possibility of set operations so always return set
            return this.maps.tagMap.get(Number(id)) || new Set();
        } else if (type == "search") {
            // possibility of set operations so always return set
            return this.maps.searchMap.get(Number(id)) || new Set();
        } else {
            return new Set();
        }
    }

    unique_sum(tags) {
        // perform union operations on all the reference ids
        // associated with each tag in tags, thus performing
        // a "unique_sum"
        let refs = new Set();
        for (const tag of tags) {
            refs = refs.union(this.tag_lookup(tag));
        }
        return refs;
    }

    section_lookup(label) {
        // find section by label
        return this.sections.find(s => s.label == label);
    }

    block_sum(blocks) {
        // compile a set of reference ids given
        // blocks to include and blocks to exclude.
        let total = new Set();
        for (const block of blocks) {
            if (block.type == "include") {
                total = total.union(block.refs);
            } else if (block.type == "exclude") {
                total = total.difference(block.refs);
            }
        }
        return total;
    }

    setRefs() {
        for (const section of this.sections) {
            for (const block of section.blocks) {
                // set the reference ids and reference id count
                // on each block in each section
                let block_tags = [];
                if (block.items) {
                    // if there are sub blocks include them in
                    // "unique_sum" calculation
                    for (const item of block.items) {
                        item.refs = this.unique_sum(item.tags);
                        item.value = item.refs.size;
                        block_tags.push(...(item.tags || []));
                    }
                }
                if (block.count_strategy == null) {
                    continue;
                } else if (block.count_strategy == "unique_sum") {
                    // perform "unique_sum" count
                    block_tags.push(...(block.tags || []));
                    block.refs = this.unique_sum(block_tags);
                    block.value = block.refs.size;
                } else {
                    // perform count based on blocks in other section
                    let prev_section = this.section_lookup(block.count_strategy);
                    block.refs = this.block_sum(prev_section.blocks);
                    block.value = block.refs.size;
                }
            }
        }
    }

    getCsrfToken() {
        return this.options.csrf;
    }
}

export default PrismaDatastore;
