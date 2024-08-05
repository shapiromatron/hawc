import _ from "lodash";
import {action, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import {NULL_VALUE} from "summary/summary/constants";

import PrismaDefaultSettings from "../prisma/PrismaDefaultSettings";

let createSectionRow = function() {
        return {
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
    createBulletedListRow = function () {
        return {
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
    createCardRow = function () {
        return {
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
    createArrowRow = function () {
        return {
            source: "",
            dest: "",
            width: 0,
            type: 0,
            color: ""
        };
    };

class PrismaStore {
    constructor(rootStore) {
        this.root = rootStore;
    }
    @observable settings = null;

    getDefaultSettings() {
        return PrismaDefaultSettings;
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

    @action.bound getTagOptions() {
        // TODO: get tag options from assessment
        return [{id:1, label: "test"}];
    }

    @action.bound getArrowOptions() {
        // TODO: gather all options for arrow start/end
        return [{ id: 1, label: "test" }];
    }

    @action.bound getLinkingOptions(key) {
        // TODO: enforce unique names for sections/boxes etc.
        // also, update this reactively when new section added?
        const options = [];
        this.settings[key].forEach(value => {
            options.push({id: value.name, label: value.name});
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    }
}

export default PrismaStore;
