import _ from "lodash";
import {action, computed, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const createSectionRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: null,
        };
    },
    createBoxRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: null,
            section: NULL_VALUE,
            box_layout: "card",
            tag: NULL_VALUE,
        };
    },
    createBulletedListRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: null,
            box: NULL_VALUE,
            tag: NULL_VALUE,
        };
    },
    createCardRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: null,
            box: NULL_VALUE,
            tag: NULL_VALUE,
        };
    },
    createArrowRow = function() {
        return {
            key: h.randomString(),
            styling: null,
            src: NULL_VALUE,
            dst: NULL_VALUE,
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
    ];

class PrismaStore {
    constructor(rootStore, data) {
        this.root = rootStore;
        this.data = data;
    }
    @observable settings = null;

    getDefaultSettings() {
        return {
            title: "Prisma Visual",
            sections: [],
            boxes: [],
            bulleted_lists: [],
            cards: [],
            arrows: [],
            styles: {
                stroke_radius: 5,
                stroke_width: 2,
                stroke_color: "#000000",
                width: 0,
                height: 0,
                border_width: 3,
                bg_color: "#ffffff",
                font_color: "#000000",
                font_size: 0.0,
                padding_x: 0,
                padding_y: 0,
                x: 0,
                y: 0,
            },
            arrow_styles: {
                arrow_type: 1,
                stroke_width: 2,
                stroke_color: "#000000",
            }
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
        const arr = this.settings[key];
        deleteArrayElement(arr, index);
        this.settings[key] = arr;
    }

    @action.bound createNewSection() {
        this.settings.sections.push(createSectionRow());
    }

    @action.bound createNewBox() {
        this.settings.boxes.push(createBoxRow());
    }

    @action.bound createNewBulletedList() {
        this.settings.bulleted_lists.push(createBulletedListRow());
    }

    @action.bound createNewCard() {
        this.settings.cards.push(createCardRow());
    }

    @action.bound createNewArrow() {
        this.settings.arrows.push(createArrowRow());
    }

    @action.bound getFilterOptions() {
        const tag_options = this.data.tags.map(tag => {
                return {id: "tag_" + tag.id, label: `TAG | ${tag.nested_name}`};
            }),
            search_options = this.data.searches.map(search => {
                return {id: "search_" + search.id, label: `SEARCH/IMPORT | ${search.title}`};
            });
        return _.flatten([{id: NULL_VALUE, label: NULL_VALUE}, tag_options, search_options]);
    }

    @action.bound getArrowOptions() {
        const section_options = this.settings.sections.map(value => {
            return {id: value.key, label: value.label};
        });
        const box_options = this.settings.boxes.map(value => {
            return {id: value.key, label: value.label};
        });
        return _.flatten([{id: NULL_VALUE, label: NULL_VALUE}, section_options, box_options]);
    }

    @action.bound getArrowTypes() {
        return ARROW_TYPES;
    }

    @action.bound getBoxLayouts() {
        return BOX_LAYOUTS;
    }

    @action.bound getLinkingOptions(key) {
        const options = this.settings[key].map(value => {
            return {id: value.key, label: value.label};
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }

    @action.bound getBoxOptions(layout_type) {
        const options = this.settings.boxes
            .filter(obj => obj.box_layout == layout_type)
            .map(value => {
                return {id: value.key, label: value.label};
            });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }

    @action.bound toggleStyling(arrayKey, index, checked) {
        if (checked) {
            // if checked, add defaults to the styling dict for this object
            this.settings[arrayKey][index].styling = this.settings.styles;
        }
        else this.settings[arrayKey][index].styling = null;
    }

    @action.bound toggleArrowStyling(index, checked) {
        if (checked) {
            // if checked, add defaults to the styling dict for this object
            this.settings.arrows[index].styling = this.settings.arrow_styles;
        }
        else this.settings.arrows[index].styling = null;
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
}

export default PrismaStore;
