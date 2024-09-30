import _ from "lodash";
import {action, computed, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const createSectionRow = function() {
        return {
            key: h.randomString(),
            label: "",
            width: 0,
            height: 0,
            border_width: 0,
            rx: 0,
            ry: 0,
            bg_color: "",
            border_color: "",
            font_color: "",
            text_style: "",
        };
    },
    createBoxRow = function() {
        return {
            key: h.randomString(),
            label: "",
            width: 0,
            height: 0,
            border_width: 0,
            rx: 0,
            ry: 0,
            bg_color: "",
            border_color: "",
            font_color: "",
            text_style: "",
            section: "",
            tag: NULL_VALUE,
        };
    },
    createBulletedListRow = function() {
        return {
            key: h.randomString(),
            label: "",
            width: 0,
            height: 0,
            border_width: 0,
            rx: 0,
            ry: 0,
            bg_color: "",
            border_color: "",
            font_color: "",
            text_style: "",
            box: "",
            tag: NULL_VALUE,
        };
    },
    createCardRow = function() {
        return {
            key: h.randomString(),
            label: "",
            width: 0,
            height: 0,
            border_width: 0,
            rx: 0,
            ry: 0,
            bg_color: "",
            border_color: "",
            font_color: "",
            text_style: "",
            box: "",
            tag: NULL_VALUE,
        };
    },
    createArrowRow = function() {
        return {
            key: h.randomString(),
            width: 0,
            type: 0,
            color: "",
            src: NULL_VALUE,
            dst: NULL_VALUE,
        };
    };

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

    @action.bound getLinkingOptions(key) {
        const options = this.settings[key].map(value => {
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
