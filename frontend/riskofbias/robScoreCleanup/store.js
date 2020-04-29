import _ from "lodash";
import {autorun, observable, computed, action, toJS} from "mobx";

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
    @observable studyScores = observable.array();
    @observable selectedStudyScores = observable.set();
    @observable studyScoresFetchTime = null;
    @observable isFetchingStudyScores = false;
    @observable visibleScoreHash = "";

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

    @action.bound fetchScores() {
        this.isFetchingStudyScores = true;
        this.clearFetchedScores();
        const {host, items, assessment_id} = this.config,
            url = h.getUrlWithAssessment(
                h.getObjectUrl(host, items.url, this.selectedMetric),
                assessment_id
            );

        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.studyScores = _.sortBy(json.scores, "study_name");
                this.studyScoresFetchTime = new Date().toISOString();
            })
            .catch(error => {
                this.error = error;
            })
            .finally(() => {
                this.isFetchingStudyScores = false;
            });
    }
    @action.bound clearFetchedScores() {
        this.studyScores = [];
        this.studyScoresFetchTime = null;
        this.selectedStudyScores = new Set();
    }

    @action.bound changeSelectedStudyScores(id, selected, score, notes) {
        if (selected) {
            this.selectedStudyScores.add(id);
            this.setFormScore(score);
            this.setFormNotes(notes);
        } else {
            this.selectedStudyScores.delete(id);
        }
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
    @action.bound clearSelectedStudyScores() {
        this.selectedStudyScores = new Set();
    }
    @action.bound selectAllStudyScores() {
        const studyScores = this.visibleStudyScores;
        this.selectedStudyScores = new Set(studyScores.map(score => score.id));
        if (studyScores.length > 0) {
            this.setFormScore(studyScores[0].score);
            this.setFormNotes(studyScores[0].notes);
        }
    }
    @action.bound setVisibleScoreHash(newScoreHash) {
        this.visibleScoreHash = newScoreHash;
    }

    @computed get visibleStudyScores() {
        let scores = this.studyScores;

        if (this.selectedScores.length > 0) {
            const selectedScores = new Set(toJS(this.selectedScores));
            scores = _.filter(scores, score => selectedScores.has(score.score));
        }

        if (this.selectedStudyTypes.length > 0) {
            const selectedStudyTypes = new Set(toJS(this.selectedStudyTypes));
            scores = _.filter(scores, score =>
                _.some(score.study_types, studyType => selectedStudyTypes.has(studyType))
            );
        }

        return scores;
    }

    // form store
    @observable formScore = null;
    @observable formNotes = "";
    @action.bound setFormScore(value) {
        this.formScore = value;
    }
    @action.bound setFormNotes(value) {
        this.formNotes = value;
    }
    @action.bound bulkUpdateSelectedStudies() {
        const ids = Array.from(this.selectedStudyScores),
            payload = {
                score: this.formScore,
                notes: this.formNotes,
            },
            opts = h.fetchBulk(this.config.csrf, payload),
            url = h.getBulkUrl(
                this.config.host,
                h.getUrlWithAssessment(this.config.items.patchUrl, this.config.assessment_id),
                ids
            );

        this.resetError();
        fetch(url, opts).then(response => {
            if (response.ok) {
                this.fetchScores();
            } else {
                response.json().then(json => {
                    this.setError(json);
                });
            }
        });
    }
}

const store = new RobCleanupStore();

autorun(() => {
    // whenever visible scores change, reset selected items
    const newScoreHash = store.visibleStudyScores.map(score => score.id.toString()).join("-");
    if (store.visibleScoreHash !== newScoreHash) {
        store.clearSelectedStudyScores();
        store.setVisibleScoreHash(newScoreHash);
    }
});

// singleton pattern
export default store;
