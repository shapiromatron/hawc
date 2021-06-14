import * as d3 from "d3";
import _ from "lodash";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

class RobTableStore {
    @observable error = null;
    @observable settings = null;
    @observable study = null;
    @observable isFetching = false;
    @observable itemsLoaded = false;
    @observable riskofbiases = [];
    @observable active = [];
    @observable final = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound setError(message) {
        this.error = message;
    }
    @action.bound resetError() {
        this.error = null;
    }

    @computed get domains() {
        return this.settings.domains.reduce(function(obj, d) {
            obj[d.id] = d;
            return obj;
        }, {});
    }

    @computed get metrics() {
        return this.settings.metrics.reduce(function(obj, m) {
            obj[m.id] = m;
            return obj;
        }, {});
    }

    @computed get metricDomains() {
        let {domains, metrics} = this;
        return this.settings.metrics.reduce(function(obj, m) {
            obj[m.id] = domains[metrics[m.id].domain_id];
            return obj;
        }, {});
    }

    @action.bound fetchSettings(assessment_id) {
        const url = `/rob/api/assessment/${assessment_id}/settings/`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.settings = data;
            });
    }

    @action.bound fetchStudy(study_id) {
        const url = `/study/api/study/${study_id}/v2/`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.study = data;
            });
    }

    @action.bound fetchFullStudyIfNeeded() {
        if (this.isFetching || this.itemsLoaded) {
            return;
        }

        this.isFetching = true;
        this.itemsLoaded = false;
        this.resetError();
        Promise.all([
            this.fetchStudy(this.config.study.id),
            this.fetchSettings(this.config.assessment_id),
        ])
            .then(d => {
                const dirtyRoBs = _.filter(this.study.riskofbiases, rob => rob.active === true),
                    domains = _.flattenDeep(
                        _.map(dirtyRoBs, riskofbias => {
                            return _.map(riskofbias.scores, score => {
                                return Object.assign({}, score, {
                                    score_symbol: this.settings.score_metadata.symbols[score.score],
                                    score_shade: this.settings.score_metadata.colors[score.score],
                                    score_description: this.settings.score_metadata.choices[
                                        score.score
                                    ],
                                    assessment_id: this.config.assessment_id,
                                    riskofbias_id: riskofbias.id,
                                    author: riskofbias.author,
                                    final: riskofbias.final,
                                    domain_name: this.metricDomains[score.metric_id].name,
                                    domain_id: this.metricDomains[score.metric_id].id,
                                    metric_name: this.metrics[score.metric_id].name,
                                    metric: this.metrics[score.metric_id],
                                });
                            });
                        })
                    ),
                    robs = d3
                        .nest()
                        .key(d => this.metricDomains[d.metric_id].name)
                        .key(d => this.metrics[d.metric_id].name)
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
            .key(d => this.metricDomains[d.metric_id].name)
            .key(d => this.metrics[d.metric_id].name)
            .entries(domains);
    }

    @computed get allRobShown() {
        return this.active && this.riskofbiases && this.active.length === this.riskofbiases.length;
    }
}

export default RobTableStore;
