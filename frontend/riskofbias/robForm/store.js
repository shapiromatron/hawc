import _ from "lodash";
import {observable, computed, action} from "mobx";

import h from "riskofbias/robTable/utils/helpers";

const updateRobScore = function(score, riskofbias) {
    return Object.assign({}, score, {
        riskofbias_id: riskofbias.id,
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
    scores = observable.array();
    editableScores = observable.array();
    nonEditableScores = observable.array();
    domainIds = observable.array();

    // computed props
    @computed get dataLoaded() {
        return this.study !== null && this.study.id !== undefined;
    }
    getScoresForDomain(domainId) {
        return this.scores.filter(score => score.metric.domain.id == domainId);
    }
    getEditableScore(scoreId) {
        return this.editableScores.filter(score => score.id === scoreId)[0];
    }

    // actions
    @action.bound setConfig(elementId) {
        this.config = JSON.parse(document.getElementById(elementId).textContent);
    }

    @action.bound fetchFullStudy() {
        this.error = null;

        let url = h.getObjectUrl(this.config.host, this.config.study.url, this.config.study.id);

        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const editableRiskOfBiasId = this.config.riskofbias.id;

                this.study = json;

                this.scores.replace(
                    _.flatten(
                        json.riskofbiases.map(riskofbias =>
                            riskofbias.scores.map(score => updateRobScore(score, riskofbias))
                        )
                    )
                );

                this.editableScores.replace(
                    _.chain(this.scores)
                        .filter(score => score.riskofbias_id === editableRiskOfBiasId)
                        .sortBy("id")
                        .value()
                );

                this.nonEditableScores.replace(
                    _.chain(this.scores)
                        .filter(score => score.riskofbias_id !== editableRiskOfBiasId)
                        .sortBy("id")
                        .value()
                );

                this.domainIds.replace(
                    _.chain(this.scores)
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
    @action.bound modifyScore() {
        console.log("notifyStateChange here");
    }
    @action.bound cancelSubmitScores() {
        window.location.href = this.config.cancelUrl;
    }
    @action.bound submitScores() {
        console.log("submitScores here");
    }
    @action.bound scoreStateChange() {
        console.log("scoreStateChange here");
    }
    @action.bound createScoreOverride(payload) {
        let url = `${this.config.riskofbias.scores_url}?assessment_id=${this.config.assessment_id}`,
            csrf = this.config.csrf;

        return fetch(url, h.fetchPost(csrf, payload, "POST"))
            .then(response => response.json())
            .then(json => {
                console.log("added!");
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
                    console.log("deleted");
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
