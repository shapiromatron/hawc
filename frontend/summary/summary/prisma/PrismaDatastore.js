import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

class PrismaDatastore {
    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
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
                    block_layout: "list",
                    blocks: boxes
                        .filter(b => b.section === section.key)
                        .map(b => {
                            return {
                                label: b.label,
                                key: b.key,
                                tags: b.tag,
                                count: b.count,
                                include: b.include,
                                exclude: b.exclude,
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

    section_lookup(key) {
        // find section by key
        return this.sections.find(s => s.key == key);
    }
    
    blocks_lookup(sectionKey,blockKeys) {
        // find blocks by section key and block keys
        return this.section_lookup(sectionKey).blocks.filter(b=>blockKeys.includes(b.key))
    }

    block_sum(include,exclude) {
        // compile a set of reference ids given
        // blocks to include and blocks to exclude.
        let total = new Set();
        for (const block of include) {
            total = total.union(block.refs);
        }
        for (const block of exclude) {
            total = total.difference(block.refs);
        }
        return total;
    }

    setRefs() {
        const skipped = [];

        for (const section of this.sections) {
            for (const block of section.blocks) {
                // set the reference ids and reference id count
                // on each block in each section
                let block_tags = [];
                if (block.sub_blocks) {
                    // if there are sub blocks include them in
                    // "unique_sum" calculation
                    for (const sub_block of block.sub_blocks) {
                        sub_block.refs = this.unique_sum(sub_block.tags);
                        sub_block.value = sub_block.refs.size;
                        block_tags.push(...(sub_block.tags || []));
                    }
                }
                if (block.count == "unique_sum") {
                    // perform "unique_sum" count
                    block_tags.push(...(block.tags || []));
                    block.refs = this.unique_sum(block_tags);
                    block.value = block.refs.size;
                } else if (block.count != null) {
                    // perform counts based on other blocks
                    // after these block counts have been computed
                    skipped.push(block)
                }
            }
        }
        for(const block of skipped) {
            // perform count based on other blocks
            let include = this.blocks_lookup(block.count,block.include),
                exclude = this.blocks_lookup(block.count,block.exclude);
            block.refs = this.block_sum(include, exclude);
            block.value = block.refs.size;
        }
    }
}

export default PrismaDatastore;
