import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

const fields = ["system", "organ", "effect", "effect_subtype", "name"];

class EndpointFormStore {
    @observable config = null;
    @observable useControlledVocabulary = null;

    constructor(config) {
        this.config = config;
        this.setUseControlledVocabulary();
    }

    setUseControlledVocabulary() {
        let toggle = {};
        const useVocab = this.canUseControlledVocabulary,
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
    endpointNameLookup(val) {
        const url = `/vocab/api/${this.config.vocabulary_url}/${val}/endpoint-name-lookup/`;

        if (!val) {
            return;
        }

        fetch(url, h.fetchGet)
            .then(resp => {
                if (resp.ok) {
                    return resp.json();
                } else {
                    throw new Error("Invalid response", resp);
                }
            })
            .then(json => {
                // set controlled vocabulary usage
                fields.map(field => {
                    this.useControlledVocabulary[field] = true;
                });
                // set values
                _.each(json, (value, key) => {
                    this.config.object[key] = value;
                });
            })
            .catch(err => {
                console.error(err);
            });
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
