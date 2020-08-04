import {action, computed, observable, toJS} from "mobx";

class EndpointFormStore {
    @observable config = null;

    constructor(config) {
        this.config = config;
    }

    @computed get useVocabulary() {
        return this.config.vocabulary !== null;
    }
}
export default EndpointFormStore;
