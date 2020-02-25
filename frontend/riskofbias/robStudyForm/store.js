import _ from "lodash";
import {observable, computed, action, toJS} from "mobx";

import {NR_KEYS} from "riskofbias/constants";
import h from "riskofbias/robTable/utils/helpers";

const updateRobScore = function(score, riskofbias) {
    return Object.assign({}, score, {
        author: riskofbias.author,
        final: riskofbias.final,
        domain_name: score.metric.domain.name,
        domain_id: score.metric.domain.id,
    });
};

class RobFormStore {
    // content
    @observable error = null;
    @observable config = null;
    @observable study = null;
    @observable overrideOptions = null;
    scores = observable.array();
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

    getScoresForDomain(domainId) {
        return this.scores.filter(score => score.metric.domain.id == domainId);
    }
    getEditableScoresForMetric(metricId) {
        return [...this.editableScores.values()].filter(score => score.metric.id == metricId);
    }
    getNonEditableScoresForMetric(metricId) {
        return this.nonEditableScores.filter(score => score.metric.id == metricId);
    }
    metricHasOverrides(metricId) {
        return _.chain(this.scores)
            .filter(score => score.metric.id == metricId)
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

    @action.bound fetchOverrideOptions() {
        let url = this.config.riskofbias.override_options_url;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.overrideOptions = json;
            })
            .catch(exception => {
                this.error = exception;
            });
    }

    @action.bound fetchFullStudy() {
        this.error = null;

        let url = h.getObjectUrl(this.config.host, this.config.study.url, this.config.study.id);

        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const editableRiskOfBiasId = this.config.riskofbias.id,
                    scores = _.flatten(
                        json.riskofbiases.map(riskofbias =>
                            riskofbias.scores.map(score => updateRobScore(score, riskofbias))
                        )
                    );

                this.study = json;

                this.scores.replace(scores);

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

                this.domainIds.replace(
                    _.chain(scores)
                        .flatMapDeep("metric.domain.id")
                        .uniq()
                        .value()
                );
            })
            .catch(exception => {
                this.error = exception;
            });
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
                        label: score.label,
                        notes: score.notes,
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
            .then(response => response.json())
            .then(() => (window.location.href = this.config.cancelUrl))
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
                this.editableScores.set(json.id, updateRobScore(json, activeRiskOfBias));
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
