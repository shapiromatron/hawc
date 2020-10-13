import * as d3 from "d3";
import _ from "lodash";
import fetch from "isomorphic-fetch";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

class RobTableStore {
    @observable error = null;
    @observable isFetching = false;
    @observable itemsLoaded = false;
    @observable riskofbiases = [];
    @observable active = [];
    @observable final = null;
    @observable name = "";
    @observable rob_response_values = [];
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
        this.itemsLoaded = false;
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
                this.active = robs;
                this.final = _.has(finalRobs, "scores") ? finalRobs.scores : [];
                this.isFetching = false;
                this.itemsLoaded = true;
            })
            .catch(error => {
                this.setError(error);
                this.isFetching = false;
                this.itemsLoaded = false;
            });
    }

    @action.bound selectDomain(domain) {
        this.active = [_.find(this.riskofbiases, {key: domain})];
    }
    @action.bound selectMetric(domain, metric) {
        let domains = _.find(this.riskofbiases, {key: domain}),
            values = _.find(domains.values, {key: metric});
        this.active = [Object.assign({}, domains, {values: [values]})];
    }
    @action.bound toggleShowAll() {
        this.active = this.allRobShown ? [] : this.riskofbiases;
    }

    @computed get formatRobForAggregateDisplay() {
        const domains = _.flattenDeep(
            _.map(this.riskofbiases, domain => {
                return _.map(domain.values, metric => {
                    return _.filter(metric.values, score => score.final);
                });
            })
        );

        return d3
            .nest()
            .key(d => d.metric.domain.name)
            .key(d => d.metric.name)
            .entries(domains);
    }

    @computed get allRobShown() {
        return this.active && this.riskofbiases && this.active.length === this.riskofbiases.length;
    }
}

export default RobTableStore;
