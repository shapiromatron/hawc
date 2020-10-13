import * as d3 from "d3";
import _ from "lodash";
import fetch from "isomorphic-fetch";
import {action, observable} from "mobx";

import h from "shared/utils/helpers";

class RobTableStore {
    @observable error = null;
    @observable isFetching = false;
    @observable itemsLoaded = false;
    @observable riskofbiases = null;
    @observable final = null;
    @observable name = "";
    @observable rob_response_values = [];
    @observable active = [];
    @observable current_score_state = {};

    constructor(config) {
        this.config = config;
    }

    @action.bound setError(message) {
        this.error = message;
    }
    @action.bound resetError() {
        this.error = null;
    }

    @action.bound fetchFullStudyIfNeeded() {
        if (this.isFetching || this.itemsLoaded) {
            return;
        }

        this.isFetching = true;
        this.resetError();
        fetch(
            h.getObjectUrl(this.config.host, this.config.study.url, this.config.study.id),
            h.fetchGet
        )
            .then(response => response.json())
            .then(study => {
                const dirtyRoBs = _.filter(study.riskofbiases, rob => rob.active === true),
                    domains = _.flattenDeep(
                        _.map(dirtyRoBs, riskofbias => {
                            return _.map(riskofbias.scores, score => {
                                return Object.assign({}, score, {
                                    riskofbias_id: riskofbias.id,
                                    author: riskofbias.author,
                                    final: riskofbias.final,
                                    domain_name: score.metric.domain.name,
                                    domain_id: score.metric.domain.id,
                                });
                            });
                        })
                    ),
                    robs = d3
                        .nest()
                        .key(d => d.metric.domain.name)
                        .key(d => d.metric.name)
                        .entries(domains),
                    finalRobs = _.find(dirtyRoBs, {final: true});

                this.riskofbiases = robs;
                this.final = _.has(finalRobs, "scores") ? finalRobs.scores : [];
            })
            .catch(error => {
                this.setError(error);
            });
    }

    @action.bound selectActive(domain, metric) {
        if (_.isEmpty(domain) | (domain === "none")) {
            this.active = [];
        } else if (domain === "all") {
            this.active = this.riskofbiases;
        } else if (metric !== undefined) {
            let domains = _.find(this.riskofbiases, {key: domain});
            let values = _.find(domains.values, {key: metric});
            this.active = [Object.assign({}, domains, {values: [values]})];
        } else {
            let domains = _.find(this.riskofbiases, {key: domain});
            this.active = domains;
        }
    }
}

export default RobTableStore;
