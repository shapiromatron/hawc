import _ from "lodash";
import {action, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const createSectionRow = function() {
        return {
            key: h.randomString(),
            name: "",
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
            name: "",
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
        };
    },
    createBulletedListRow = function() {
        return {
            key: h.randomString(),
            name: "",
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
        };
    },
    createCardRow = function() {
        return {
            key: h.randomString(),
            name: "",
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
        };
    },
    createArrowRow = function() {
        return {
            key: h.randomString(),
            source: "",
            dest: "",
            width: 0,
            type: 0,
            color: "",
        };
    };

class PrismaStore {
    constructor(rootStore, count_data) {
        this.root = rootStore;
        this.count_data = count_data;
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

    @action.bound getCountOptions() {
        const tag_options = this.count_data.tags.map(tag => {
            return {id: "tag_" + tag.id, label: "TAG | " + tag.nested_name};
        });
        const search_options = this.count_data.searches.map(search => {
            return {id: "search_" + search.id, label: "IMPORT | " + search.title};
        });
        const options = Object.assign([], tag_options, search_options);
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }

    @action.bound getArrowOptions() {
        const options = this.settings.boxes.map(value => {
            return {id: value.key, label: value.name};
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }

    @action.bound getLinkingOptions(key) {
        const options = this.settings[key].map(value => {
            return {id: value.key, label: value.name};
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }
}

export default PrismaStore;
