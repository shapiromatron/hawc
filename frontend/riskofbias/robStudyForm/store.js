import _ from "lodash";
import {observable, computed, action} from "mobx";

import {NR_KEYS} from "riskofbias/constants";
import h from "shared/utils/helpers";

class RobFormStore {
    // content
    @observable error = null;
    @observable config = null;
    @observable study = null;
    @observable settings = null;
    @observable overrideOptions = null;
    editableScores = observable.map();
    nonEditableScores = observable.array();
    domainIds = observable.array();

    // computed props
    @computed get dataLoaded() {
        return this.study !== null && this.overrideOptions !== null;
    }
    @computed get activeRiskOfBias() {
        return _.find(this.study.riskofbiases, {id: this.config.riskofbias.id});
    }
    @computed get numIncompleteScores() {
        return [...this.editableScores.values()].filter(score => {
            return (
                _.includes(NR_KEYS, score.score) && score.notes.replace(/<\/?[^>]+(>|$)/g, "") == ""
            );
        }).length;
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

    updateRobScore(score, riskofbias, overrideOptions) {
        let overrideDataTypeValue;
        if (score.is_default) {
            overrideDataTypeValue = null;
        } else if (score.overridden_objects.length > 0) {
            overrideDataTypeValue = score.overridden_objects[0].content_type_name;
        } else {
            overrideDataTypeValue = _.keys(overrideOptions)[0] || null;
        }
        return Object.assign({}, score, {
            overrideDataTypeValue,
            author: riskofbias.author,
            final: riskofbias.final,
            score_symbol: this.settings.score_metadata.symbols[score.score],
            score_shade: this.settings.score_metadata.colors[score.score],
            score_description: this.settings.score_metadata.choices[score.score],
        });
    }

    getMetricIds(domainId) {
        return _.uniq(
            [...store.editableScores.values()].reduce(function(array, score) {
                store.metricDomains[score.metric_id].id == domainId
                    ? array.push(score.metric_id)
                    : null;
                return array;
            }, [])
        );
    }

    getEditableScoresForMetric(metricId) {
        return [...this.editableScores.values()].filter(score => score.metric_id == metricId);
    }
    getNonEditableScoresForMetric(metricId) {
        return this.nonEditableScores.filter(score => score.metric_id == metricId);
    }

    nonEditableMetricHasOverrides(metricId) {
        return _.chain(this.getNonEditableScoresForMetric(metricId))
            .map(score => score.is_default === false)
            .some()
            .value();
    }
    editableMetricHasOverrides(metricId) {
        return _.chain(this.getEditableScoresForMetric(metricId))
            .map(score => score.is_default === false)
            .some()
            .value();
    }
    getEditableScore(scoreId) {
        if (!this.editableScores.has(scoreId)) {
            throw `Score ${scoreId} does not exist.`;
        }
        return this.editableScores.get(scoreId);
    }

    // actions
    @action.bound setConfig(elementId) {
        this.config = JSON.parse(document.getElementById(elementId).textContent);
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

    @action.bound fetchFormData() {
        let override_options_url = this.config.riskofbias.override_options_url;

        Promise.all([
            fetch(override_options_url, h.fetchGet).then(response => response.json()),
            this.fetchStudy(this.config.study.id),
            this.fetchSettings(this.config.assessment_id),
        ])
            .then(data => {
                // only set options which have data
                let overrideOptions = {};
                _.each(data[0], (value, key) => {
                    if (value.length > 0) {
                        overrideOptions[key] = value;
                    }
                });
                this.overrideOptions = overrideOptions;

                const editableRiskOfBiasId = this.config.riskofbias.id,
                    scores = _.flatten(
                        this.study.riskofbiases
                            .filter(riskofbias => riskofbias.active === true)
                            .map(riskofbias =>
                                riskofbias.scores.map(score =>
                                    this.updateRobScore(score, riskofbias, overrideOptions)
                                )
                            )
                    );

                scores
                    .filter(score => score.riskofbias_id === editableRiskOfBiasId)
                    .forEach(score => {
                        this.editableScores.set(score.id, score);
                    });

                this.nonEditableScores.replace(
                    _.chain(scores)
                        .filter(score => score.riskofbias_id !== editableRiskOfBiasId)
                        .sortBy("id")
                        .value()
                );

                this.domainIds.replace(_.uniq(scores.map(s => this.metricDomains[s.metric_id].id)));
            })
            .catch(exception => {
                this.error = exception;
            });
    }

    @action.bound updateFormState(scoreId, key, value) {
        this.getEditableScore(scoreId)[key] = value;
    }

    // CRUD actions
    @action.bound cancelSubmitScores() {
        window.location.href = this.config.cancelUrl;
    }
    @action.bound submitScores() {
        const payload = {
                id: this.config.riskofbias.id,
                scores: [...this.editableScores.values()].map(score => {
                    return {
                        id: score.id,
                        score: score.score,
                        bias_direction: score.bias_direction,
                        label: score.label,
                        notes: score.notes,
                        overridden_objects: score.overridden_objects.map(obj => {
                            return {
                                object_id: obj.object_id,
                                content_type_name: obj.content_type_name,
                            };
                        }),
                    };
                }),
            },
            opts = h.fetchPost(this.config.csrf, payload, "PATCH"),
            url = `${h.getObjectUrl(
                this.config.host,
                this.config.riskofbias.url,
                this.config.riskofbias.id
            )}`;
        // catch errors that are not reported cleanly on the backend
        // missing scores
        const missingScores = payload.scores.filter(score => isNaN(score.score));
        if (missingScores.length > 0) {
            this.error = `Missing ${missingScores.length} score(s).`;
            return;
        }

        this.error = null;
        return fetch(url, opts)
            .then(response => {
                if (response.ok) {
                    window.location.href = this.config.cancelUrl;
                } else {
                    response.text().then(text => {
                        this.error = text;
                    });
                }
            })
            .catch(error => {
                this.error = error;
            });
    }
    @action.bound createScoreOverride(payload) {
        let url = `${this.config.riskofbias.scores_url}?assessment_id=${this.config.assessment_id}`,
            csrf = this.config.csrf,
            activeRiskOfBias = this.activeRiskOfBias;

        return fetch(url, h.fetchPost(csrf, payload, "POST"))
            .then(response => response.json())
            .then(json => {
                this.editableScores.set(
                    json.id,
                    this.updateRobScore(json, activeRiskOfBias, this.overrideOptions)
                );
            })
            .catch(error => {
                this.error = error;
            });
    }
    @action.bound deleteScoreOverride(scoreId) {
        let url = `${this.config.riskofbias.scores_url}${scoreId}/?assessment_id=${this.config.assessment_id}&ids=${scoreId}`,
            csrf = this.config.csrf;

        return fetch(url, h.fetchDelete(csrf))
            .then(response => {
                if (response.status === 204) {
                    this.editableScores.delete(scoreId);
                }
            })
            .catch(error => {
                this.error = error;
            });
    }
}

const store = new RobFormStore();

// singleton pattern
export default store;
