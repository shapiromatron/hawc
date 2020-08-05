import _ from "lodash";
import {action, computed, observable} from "mobx";

class EndpointFormStore {
    @observable config = null;
    @observable useControlledVocabulary = null;

    constructor(config) {
        this.config = config;
        this.setUseControlledVocabulary();
    }

    setUseControlledVocabulary() {
        let toggle = {};
        const fields = ["system", "organ", "effect", "effect_subtype", "name"],
            useVocab = this.canUseControlledVocabulary,
            {object} = this.config;
        _.forEach(fields, function(field) {
            // default case
            toggle[field] = useVocab;
            // special case where we've already specified a custom value
            if (toggle[field] && object[field] != "" && object[field + "_term_id"] == null) {
                toggle[field] = false;
            }
        });
        this.useControlledVocabulary = toggle;
    }

    @computed get canUseControlledVocabulary() {
        return this.config.vocabulary !== null;
    }

    @action.bound
    toggleUseControlledVocabulary(termTextField) {
        this.useControlledVocabulary[termTextField] = !this.useControlledVocabulary[termTextField];
    }

    @action.bound
    setObjectField(termTextField, value) {
        this.config.object[termTextField] = value;
    }
}
export default EndpointFormStore;
