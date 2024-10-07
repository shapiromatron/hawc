import _ from "lodash";
import {action, computed, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const createSectionRow = function() {
        return {
            key: h.randomString(),
            label: "",
            use_style_overrides: false,
            styling: null,
        };
    },
    createBoxRow = function(firstSection) {
        return {
            key: h.randomString(),
            label: "",
            use_style_overrides: false,
            styling: null,
            section: firstSection || NULL_VALUE,
            box_layout: "card",
            count_strategy: "unique_sum",
            count_filters: [],
            count_include: [],
            count_exclude: [],
            items: [],
        };
    },
    createNewBoxItem = function() {
        return {
            key: h.randomString(),
            label: "",
            count_filters: [],
        };
    },
    createArrowRow = function(firstSection) {
        return {
            key: h.randomString(),
            use_style_overrides: false,
            styling: null,
            src: firstSection || NULL_VALUE,
            dst: firstSection || NULL_VALUE,
        };
    },
    ARROW_TYPES = [
        {id: 1, label: "Type 1"},
        {id: 2, label: "Type 2"},
        {id: 3, label: "Type 3"},
        {id: 5, label: "Type 5"},
        {id: 10, label: "Type 10"},
        {id: 11, label: "Type 11"},
        {id: 13, label: "Type 13"},
    ],
    BOX_LAYOUTS = [
        {id: "card", label: "Card"},
        {id: "list", label: "List"},
    ];

class PrismaStore {
    constructor(rootStore, data) {
        this.root = rootStore;
        this.data = data;
    }
    @observable settings = null;

    getDefaultSettings() {
        return {
            sections: [],
            boxes: [],
            arrows: [],
            styles: {
                spacing_x: 30,
                spacing_y: 50,
                box: {
                    stroke_radius: 5,
                    stroke_width: 2,
                    stroke_color: "#000000",
                    width: 0,
                    height: 0,
                    bg_color: "#ffffff",
                    font_color: "#000000",
                    font_size: 0.0,
                    padding_x: 0,
                    padding_y: 0,
                    x: 0,
                    y: 0,
                },
                section: {
                    stroke_radius: 5,
                    stroke_width: 2,
                    stroke_color: "#000000",
                    width: 0,
                    height: 0,
                    bg_color: "#efefef",
                    font_color: "#000000",
                    font_size: 0.0,
                    padding_x: 0,
                    padding_y: 0,
                    x: 0,
                    y: 0,
                },
                arrow: {
                    arrow_type: 1,
                    stroke_width: 2,
                    stroke_color: "#000000",
                    force_vertical: false,
                },
            },
        };
    }

    @action.bound changeSettings(path, value) {
        _.set(this.settings, path, value);
    }

    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }

    @action.bound changeArraySettings(arrayKey, index, key, value) {
        this.settings[arrayKey][index][key] = value;
    }

    @action.bound changeStylingSettings(arrayKey, index, key, value) {
        this.settings[arrayKey][index].styling[key] = value;
    }

    @action.bound deleteArrayElement(key, index) {
        const arr = _.get(this.settings, key);
        deleteArrayElement(arr, index);
        _.set(this.settings, key, arr);
    }

    @action.bound createNewSection() {
        this.settings.sections.push(createSectionRow());
    }

    @action.bound createNewBox() {
        const firstSection = this.settings.sections[0].key;
        this.settings.boxes.push(createBoxRow(firstSection));
    }

    @action.bound createNewBoxItem(boxIndex) {
        this.settings.boxes[boxIndex].items.push(createNewBoxItem());
    }

    @computed get getBoxLayouts() {
        return BOX_LAYOUTS;
    }

    @action.bound createNewArrow() {
        const firstSection = this.settings.sections[0].key;
        this.settings.arrows.push(createArrowRow(firstSection));
    }

    @computed get getCountStrategies() {
        return [{id: "unique_sum", label: "Unique sum"}].concat(
            this.settings.sections.map(s => ({id: s.key, label: s.label}))
        );
    }

    @action.bound getCountBlocks(block) {
        return this.settings.boxes
            .filter(b => b.section == block.count_strategy && b.count_strategy == "unique_sum")
            .map(b => ({id: b.key, label: b.label}));
    }

    @computed get getCountFilters() {
        const tag_options = this.data.tags.map(tag => {
                return {id: "tag_" + tag.id, label: `TAG | ${tag.nested_name}`};
            }),
            search_options = this.data.searches.map(search => {
                return {id: "search_" + search.id, label: `SEARCH/IMPORT | ${search.title}`};
            });
        return tag_options.concat(search_options);
    }

    @computed get getArrowOptions() {
        const opts = [];
        this.settings.sections.forEach(section => {
            opts.push({id: section.key, label: section.label});
            opts.push(
                this.settings.boxes
                    .filter(b => b.section === section.key)
                    .map(b => {
                        return {id: b.key, label: `${section.label} ➤ ${b.label}`};
                    })
            );
        });
        return _.flatten(opts);
    }

    @computed get getArrowTypes() {
        return ARROW_TYPES;
    }

    @computed get getSectionOptions() {
        return this.settings.sections.map(value => {
            return {id: value.key, label: value.label};
        });
    }

    @action.bound toggleStyling(arrayKey, index, checked) {
        const {styles} = this.settings;
        if (checked && this.settings[arrayKey][index].styling == null) {
            // if checked for the first time, add defaults to the styling dict for this object
            switch (arrayKey) {
                case "sections":
                    this.settings[arrayKey][index].styling = _.cloneDeep(styles.section);
                    break;
                case "boxes":
                    this.settings[arrayKey][index].styling = _.cloneDeep(styles.box);
                    break;
                case "arrows":
                    this.settings[arrayKey][index].styling = _.cloneDeep(styles.arrow);
                    break;
            }
        }
        this.settings[arrayKey][index].use_style_overrides = checked;
    }

    @computed get sectionMapping() {
        const mapping = {};
        this.settings.sections.forEach(section => (mapping[section.key] = section.label));
        return mapping;
    }

    @computed get arrowMapping() {
        const mapping = {};
        this.settings.sections.forEach(section => (mapping[section.key] = section.label));
        this.settings.boxes.forEach(section => (mapping[section.key] = section.label));
        return mapping;
    }

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    // active tab
    @observable activeTab = 0;
    @action.bound changeActiveTab(index) {
        this.activeTab = index;
        return true;
    }
}

export default PrismaStore;
