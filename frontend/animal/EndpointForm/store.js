import {action, computed, observable} from "mobx";

class EndpointFormStore {
    @observable config = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound
    setObjectField(termTextField, value) {
        this.config.object[termTextField] = value;
    }

    @computed get useVocabulary() {
        return this.config.vocabulary !== null;
    }
}
export default EndpointFormStore;
