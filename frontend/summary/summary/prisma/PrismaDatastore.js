import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";

class PrismaDatastore {
    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
        this.createMaps();
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
                                count: "unique_sum",
                                value: 123,
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

        this.maps.tagMap = this.dataset.reference_tag_pairs.reduce(
            (map, pair)=>map.set(pair.tag_id,map.has(pair.tag_id)?map.get(pair.tag_id).add(pair.reference_id):new Set([pair.reference_id])),
            new Map()
        )

        this.maps.searchMap = this.dataset.reference_search_pairs.reduce(
            (map, pair)=>map.set(pair.search_id,map.has(pair.search_id)?map.get(pair.search_id).add(pair.reference_id):new Set([pair.reference_id])),
            new Map()
        )

    }

    tag_lookup(tag){
        let [type,id] = tag.split("_")
        if(type == "tag") {
            return this.maps.tagMap.get(Number(id)) || new Set()
        }
        else if(type == "search") {
            return this.maps.searchMap.get(Number(id)) || new Set()
        }
        else {
            return new Set()
        }
    }

    unique_sum(tags){
        let refs = new Set();
        for(const tag of tags){
            refs = refs.union(this.tag_lookup(tag))
        }
        return refs
    }

    section_lookup(label){
        return this.data.find(s=>s.label == label)
    }

    block_sum(blocks){
        let total = new Set();
        for(const block of blocks){
            if(block.type == "include") {
                total = total.union(block.refs);
            }
            else if(block.type == "exclude") {
                total = total.difference(block.refs);
            }
        }
        return total
    }

    setRefs() {
        for(const section of this.sections) {
            for(const block of section.blocks) {
                let block_tags = [];
                if(block.sub_blocks) {
                    for(const sub_block of block.sub_blocks ) {
                        sub_block.refs = this.unique_sum(sub_block.tags);
                        sub_block.value = sub_block.refs.size;
                        block_tags.push(...sub_block.tags||[]);
                    }
                }
                if(block.count == null) {
                    continue;
                }
                else if(block.count == "unique_sum") {
                    block_tags.push(...block.tags||[]);
                    block.refs = this.unique_sum(block_tags);
                    block.value = block.refs.size;
                }
                else {
                    let prev_section = this.section_lookup(block.count);
                    block.refs = this.block_sum(prev_section.blocks);
                    block.value = block.refs.size;
                }
            }
        }
    }












}

export default PrismaDatastore;
