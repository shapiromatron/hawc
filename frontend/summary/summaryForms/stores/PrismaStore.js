import _ from "lodash";
import {action, observable} from "mobx";

class PrismaStore {
    constructor(rootStore) {
        this.root = rootStore;
    }
    @observable settings = null;

    getDefaultSettings() {
        return {
            title: "hello prisma",
        };
    }

    @action.bound changeSettings(path, value) {
        _.set(this.settings, path, value);
    }

    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }
}

export default PrismaStore;
