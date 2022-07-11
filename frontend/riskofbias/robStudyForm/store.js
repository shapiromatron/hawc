import _ from "lodash";
import {observable, computed, action} from "mobx";

import {NR_KEYS} from "riskofbias/constants";
import h from "shared/utils/helpers";

import StudyRobStore from "../stores/StudyRobStore";

class RobFormStore extends StudyRobStore {
    constructor(config) {
        super();
        this.config = config;
    }

    // content
    @observable error = null;
    @observable overrideOptions = null;
    editableScores = observable.array();
    nonEditableScores = observable.array();
    domainIds = observable.array();

    // computed props
    @computed get dataLoaded() {
        return this.study !== null && this.overrideOptions !== null;
    }
    @computed get activeRiskOfBias() {
        return _.find(this.activeRobs, {id: this.config.riskofbias.id});
    }
    @computed get numIncompleteScores() {
        return this.editableScores.filter(score => {
            return (
                _.includes(NR_KEYS, score.score) && score.notes.replace(/<\/?[^>]+(>|$)/g, "") == ""
            );
        }).length;
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

    @action.bound getMetricIds(domainId) {
        return _.chain(this.editableScores)
            .filter(score => this.metricDomains[score.metric_id].id == domainId)
            .map(score => score.metric_id)
            .uniq()
            .value();
    }

    getEditableScoresForMetric(metricId) {
        return this.editableScores.filter(score => score.metric_id == metricId);
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

    // actions
    @action.bound fetchFormData() {
        let override_options_url = this.config.riskofbias.override_options_url;

        Promise.all([
            fetch(override_options_url, h.fetchGet).then(response => response.json()),
            this.fetchStudy(this.config.study.id),
            this.fetchSettings(this.config.assessment_id),
            this.fetchRobStudy(this.config.study.id),
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
                    editableScores = _.chain(this.activeRobs)
                        .filter(rob => rob.id === editableRiskOfBiasId)
                        .map(riskofbias =>
                            riskofbias.scores.map(score =>
                                this.updateRobScore(score, riskofbias, overrideOptions)
                            )
                        )
                        .flatten()
                        .value(),
                    nonEditableScores = _.chain(this.activeRobs)
                        .filter(rob => rob.id !== editableRiskOfBiasId)
                        .filter(rob => rob.active & !rob.final)
                        .map(riskofbias =>
                            riskofbias.scores.map(score =>
                                this.updateRobScore(score, riskofbias, overrideOptions)
                            )
                        )
                        .flatten()
                        .sortBy("id")
                        .value();

                this.editableScores.replace(editableScores);
                this.nonEditableScores.replace(nonEditableScores);
                this.domainIds.replace(
                    _.uniq(editableScores.map(s => this.metricDomains[s.metric_id].id))
                );
            })
            .catch(exception => {
                this.error = exception;
            });
    }

    @action.bound updateScoreState(score, key, value) {
        score[key] = value;
    }

    // CRUD actions
    @action.bound cancelSubmitScores() {
        window.location.href = this.config.cancelUrl;
    }
    @action.bound submitScores(redirect) {
        const payload = {
                id: this.config.riskofbias.id,
                scores: this.editableScores.map(score => {
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

        this.error = null;
        return fetch(url, opts)
            .then(response => {
                if (response.ok && redirect) {
                    window.location.href = this.config.cancelUrl;
                } else if (!response.ok) {
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
                this.editableScores.push(
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
                    this.editableScores.replace(this.editableScores.filter(s => s.id !== scoreId));
                }
            })
            .catch(error => {
                this.error = error;
            });
    }
}

export default RobFormStore;
