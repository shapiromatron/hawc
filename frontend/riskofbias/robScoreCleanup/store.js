import _ from "lodash";
import {observable, computed, action} from "mobx";

import h from "shared/utils/helpers";
import {SCORE_TEXT_DESCRIPTION} from "../constants";

class RobCleanupStore {
    // content
    @observable config = null;
    @observable error = null;
    @observable metricOptions = null;
    @observable scoreOptions = null;
    @observable studyTypeOptions = null;
    @observable selectedMetric = null;
    @observable selectedScores = observable.array();
    @observable selectedStudyTypes = observable.array();

    // computed
    @computed get isLoading() {
        return (
            this.metricOptions === null ||
            this.scoreOptions === null ||
            this.studyTypeOptions === null
        );
    }

    // actions: config
    @action.bound setConfig(elementId) {
        this.config = JSON.parse(document.getElementById(elementId).textContent);
    }

    // actions: errors
    @action.bound resetError() {
        this.error = null;
    }
    @action.bound setError(msg) {
        this.error = msg;
    }

    // actions: metrics
    @action.bound fetchMetricOptions() {
        const {host, metrics, assessment_id} = this.config,
            url = h.getUrlWithAssessment(h.getListUrl(host, metrics.url), assessment_id);

        this.resetError();
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.metricOptions = json;
                this.selectedMetric = json[0].id;
            })
            .catch(error => {
                this.setError(error);
            });
    }
    @action.bound changeSelectedMetric(value) {
        this.selectedMetric = value;
    }

    // actions: scores
    @action.bound fetchScoreOptions() {
        const {host, scores, assessment_id} = this.config,
            url = h.getUrlWithAssessment(h.getListUrl(host, scores.url), assessment_id),
            formatScoreOptions = function(choices) {
                return choices.map(choice => {
                    return {id: choice, value: SCORE_TEXT_DESCRIPTION[choice]};
                });
            };

        this.resetError();
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => formatScoreOptions(json))
            .then(json => {
                this.scoreOptions = json;
            })
            .catch(error => {
                this.error = this.setError(error);
            });
    }
    @action.bound changeSelectedScores(values) {
        this.selectedScores = values;
    }

    // actions: studies
    @action.bound fetchStudyTypeOptions() {
        const {host, studyTypes, assessment_id} = this.config,
            url = h.getUrlWithAssessment(h.getListUrl(host, studyTypes.url), assessment_id);

        this.resetError();
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.studyTypeOptions = json;
            })
            .catch(error => {
                this.setError(error);
            });
    }
    @action.bound changeSelectedStudyType(studyTypes) {
        this.selectedStudyTypes = studyTypes;
    }
}

const store = new RobCleanupStore();

// singleton pattern
export default store;
