import _ from "lodash";
import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const mapStyles = function (styles) {
        return {
            x: styles.x,
            y: styles.y,
            width: styles.width,
            height: styles.height,
            "text-padding-x": styles.padding_x,
            "text-padding-y": styles.padding_y,
            "text-color": "#styles",
            "text-style": "styles",
            "text-size": styles.font_size,
            "bg-color": styles.bg_color,
            stroke: styles.border_color,
            "stroke-width": styles.border_width,
            rx: styles.border_radius,
            ry: styles.border_radius,
        };
    },
    mapArrowStyles = function (styles) {
        return {
            "arrow-color": styles["color"],
            "arrow-width": styles["width"],
            "arrow-type": styles["arrow_type"],
            "arrow-force-vertical": styles["force_vertical"],
        };
    };

class PrismaDatastore {
    constructor(settings, dataset, config) {
        this.settings = settings;
        this.dataset = dataset;
        this.config = config;
        this.createFilterMaps();
        this.sections = this.getDiagramSections();
        this.setRefs();
        this.settingsHash = h.hashString(JSON.stringify(this.settings));
        this.modal = new HAWCModal();
    }

    getDiagramSections() {
        const {sections, boxes, styles} = this.settings;
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
                                box_layout: b.box_layout,
                                count_strategy: b.count_strategy,
                                count_filters: b.count_filters,
                                count_include: b.count_include,
                                count_exclude: b.count_exclude,
                                styles: mapStyles(b.use_style_overrides ? b.styles : styles.box),
                                items: b.items,
                            };
                        }),
                    styles: mapStyles(
                        section.use_style_overrides ? section.styles : styles.section
                    ),
                };
            });
    }

    getConnections() {
        const {arrows, styles} = this.settings;
        return _.cloneDeep(arrows)
            .filter(a => a.src !== NULL_VALUE && a.dst !== NULL_VALUE)
            .map(a => {
                a.styles = mapArrowStyles(a.use_style_overrides ? a.styles : styles.arrow);
                return a;
            });
    }

    createFilterMaps() {
        this.filterMaps = {};

        // for each reference-tag pair we are adding the reference id
        // to the set associated with the tag id in our tag map
        this.filterMaps.tagMap = this.dataset.reference_tag_pairs.reduce(
            (map, pair) =>
                map.set(
                    pair.tag_id,
                    map.has(pair.tag_id)
                        ? map.get(pair.tag_id).add(pair.reference_id)
                        : new Set([pair.reference_id])
                ),
            new Map()
        );
        this.updateTagMap();
        // for each reference-search pair we are adding the reference id
        // to the set associated with the search id in our search map
        this.filterMaps.searchMap = this.dataset.reference_search_pairs.reduce(
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
                    this.filterMaps.tagMap.set(
                        tag.id,
                        (this.filterMaps.tagMap.get(tag.id) || new Set()).union(
                            this.filterMaps.tagMap.get(nextTag.id) || new Set()
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

    filter_lookup(filter) {
        // filter identifiers have the form "{type}_{id}",
        // where "type" can be tag or search
        // this function splits the identifier and uses the metadata
        // to retrieve the set of reference ids associated with it
        // from the relevant map
        let [type, id] = filter.split("_");
        if (type == "tag") {
            // possibility of set operations so always return set
            return this.filterMaps.tagMap.get(Number(id)) || new Set();
        } else if (type == "search") {
            // possibility of set operations so always return set
            return this.filterMaps.searchMap.get(Number(id)) || new Set();
        } else {
            return new Set();
        }
    }

    unique_sum(filters) {
        // perform union operations on all the reference ids
        // associated with each filter in filters, thus performing
        // a "unique_sum"
        let refs = new Set();
        for (const filter of filters) {
            refs = refs.union(this.filter_lookup(filter));
        }
        return refs;
    }

    section_lookup(key) {
        // find section by label
        return this.sections.find(s => s.key == key);
    }

    blocks_lookup(sectionKey, blockKeys) {
        // find blocks by section key and block keys
        return this.section_lookup(sectionKey).blocks.filter(b => blockKeys.includes(b.key));
    }

    block_sum(include, exclude) {
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

    getCsrfToken() {
        return this.config.csrf;
    }

    setRefs() {
        const skipped = [];
        for (const section of this.sections) {
            for (const block of section.blocks) {
                // set the reference ids and reference id count
                // on each block in each section
                if (block.box_layout == "list") {
                    // if there are sub blocks include them in
                    // "unique_sum" calculation
                    let block_filters = [];
                    for (const item of block.items) {
                        item.refs = this.unique_sum(item.count_filters);
                        item.value = item.refs.size;
                        block_filters.push(...item.count_filters);
                    }
                    block.refs = this.unique_sum(block_filters);
                    block.value = block.refs.size;
                } else if (block.count_strategy == "unique_sum") {
                    // perform "unique_sum" count
                    block.refs = this.unique_sum(block.count_filters);
                    block.value = block.refs.size;
                } else if (block.count_strategy != null) {
                    // perform counts based on other blocks
                    // after these block counts have been computed
                    skipped.push(block);
                }
            }
        }
        for (const block of skipped) {
            // perform count based on other blocks
            let include = this.blocks_lookup(block.count_strategy, block.count_include),
                exclude = this.blocks_lookup(block.count_strategy, block.count_exclude);
            block.refs = this.block_sum(include, exclude);
            block.value = block.refs.size;
        }
    }

    getReferenceDetailId() {
        return `${this.settingsHash}-prisma-reference-list`;
    }
}

export default PrismaDatastore;
