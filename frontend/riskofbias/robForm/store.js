import _ from "lodash";
import {observable, computed, action, createTransformer} from "mobx";

import h from "riskofbias/robTable/utils/helpers";

class RobFormStore {
    // content
    @observable error = null;
    @observable config = null;
    @observable study = null;
    scores = observable.array();
    domainIds = observable.array();

    // computed props
    @computed get dataLoaded() {
        return this.study !== null && this.study.id !== undefined;
    }
    getScoresForDomain(domainId) {
        return this.scores.filter(score => score.metric.domain.id == domainId);
    }
    getMetricsForDomain(metricId) {
        return this.scores.filter(score => score.metric.id == metricId);
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
                this.study = json;
                this.scores.replace(_.flatMapDeep(json.riskofbiases, "scores"));
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
    @action.bound cancelSubmitScores() {
        console.log("cancelSubmitScores here");
        window.location.href = this.config.cancelUrl;
    }
    @action.bound submitScores() {
        console.log("submitScores here");
    }
    @action.bound scoreStateChange() {
        console.log("scoreStateChange here");
    }
    @action.bound createScoreOverride() {
        console.log("createScoreOverride here");
    }
    @action.bound deleteScoreOverride() {
        console.log("deleteScoreOverride here");
    }
}

const store = new RobFormStore();

// singleton pattern
export default store;
