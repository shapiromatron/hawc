import _ from "lodash";
import {action, computed, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const createSectionRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: {
                width: 0,
                height: 0,
                border_width: 3,
                rx: 20,
                ry: 20,
                bg_color: "#ffffff",
                border_color: "#000000",
                font_color: "#000000",
                bold: false,
                font_size: 0.0,
                padding_x: 0,
                padding_y: 0,
                x: 0,
                y: 0,
            },
        };
    },
    createBoxRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: {
                width: 0,
                height: 0,
                border_width: 3,
                rx: 20,
                ry: 20,
                bg_color: "#ffffff",
                border_color: "#000000",
                font_color: "#000000",
                bold: false,
                font_size: 0.0,
                padding_x: 0,
                padding_y: 0,
                x: 0,
                y: 0,
            },
            section: "",
            box_layout: "card",
            tag: NULL_VALUE,
        };
    },
    createBulletedListRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: {
                width: 0,
                height: 0,
                bg_color: "#ffffff",
                font_color: "#000000",
                bold: false,
                font_size: 0.0,
                padding_x: 0,
                padding_y: 0,
            },
            box: "",
            tag: NULL_VALUE,
        };
    },
    createCardRow = function() {
        return {
            key: h.randomString(),
            label: "",
            styling: {
                width: 0,
                height: 0,
                border_width: 3,
                rx: 20,
                ry: 20,
                bg_color: "#ffffff",
                border_color: "#000000",
                font_color: "#000000",
                bold: false,
                font_size: 0.0,
                padding_x: 0,
                padding_y: 0,
                x: 0,
                y: 0,
            },
            box: "",
            tag: NULL_VALUE,
        };
    },
    createArrowRow = function() {
        return {
            key: h.randomString(),
            styling: {
                width: 2,
                type: 1,
                color: "",
                force_vertical: false,
            },
            src: NULL_VALUE,
            dst: NULL_VALUE,
        };
    },
    ARROW_TYPES = [
        {id: 1, label: "1"},
        {id: 2, label: "2"},
        {id: 3, label: "3"},
        {id: 5, label: "5"},
        {id: 10, label: "10"},
        {id: 11, label: "11"},
        {id: 13, label: "13"},
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
            title: "Prisma Visual",
            sections: [],
            boxes: [],
            bulleted_lists: [],
            cards: [],
            arrows: [],
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
        this.settings[arrayKey][index]["styling"][key] = value;
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
        const options = this.settings.boxes.map(value => {
            return {id: value.key, label: value.label};
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
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

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }
}

export default PrismaStore;
