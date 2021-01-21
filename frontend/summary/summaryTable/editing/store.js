import _ from "lodash";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

class SummaryTableEditStore {
    @observable tableObject = null; // string-representation to be submitted
    @observable formErrors = {};

    constructor(config) {
        let tableObject = _.cloneDeep(config.initial);
        tableObject.content = JSON.stringify(tableObject.content);

        this.config = config;
        this.tableObject = tableObject;
    }

    @action.bound updateContent(field, value) {
        this.tableObject[field] = value;
    }
    @action.bound handleSubmit() {
        const url = this.config.save_url,
            verb = this.isCreate ? "POST" : "PATCH",
            getPayload = () => {
                let data = _.cloneDeep(this.tableObject);
                data.assessment = this.config.assessment_id;
                data.content = JSON.parse(data.content); // convert str -> JSON
                return data;
            },
            data = getPayload();

        this.formErrors = {};
        h.handleSubmit(
            url,
            verb,
            this.config.csrf,
            data,
            item => {
                this.formErrors = {};
                window.location.href = item.url;
            },
            errors => {
                this.formErrors = errors;
            }
        );
    }

    @computed get isCreate() {
        return this.config.is_create;
    }
    @computed get cancelUrl() {
        return this.config.cancel_url;
    }
}

export default SummaryTableEditStore;
