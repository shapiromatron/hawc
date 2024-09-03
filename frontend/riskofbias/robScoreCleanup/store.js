import _ from "lodash";
import {action, autorun, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

import {fetchRobSettings, SCORE_TEXT_DESCRIPTION} from "../constants";

class RobCleanupStore {
    constructor(config) {
        this.config = config;
    }

    // content
    @observable error = null;
    @observable isFetchingStudyScores = false;
    @observable metrics = observable.array();
    @observable selectedMetric = null;
    @observable selectedScores = observable.array();
    @observable selectedStudyScores = observable.set();
    @observable selectedStudyTypes = observable.array();
    @observable settings = null;
    @observable studyScores = observable.array();
    @observable studyScoresFetchTime = null;
    @observable studyTypeOptions = null;
    @observable visibleScoreHash = "";

    // errors
    @action.bound resetError() {
        this.error = null;
    }
    @action.bound setError(msg) {
        this.error = msg;
    }

    // studyType
    @action.bound fetchStudyTypes() {
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
    @computed get hasStudyTypes() {
        return this.studyTypeOptions !== null;
    }
    @computed get studyTypeChoices() {
        return this.studyTypeOptions.map(d => {
            return {id: d, label: h.caseToWords(d)};
        });
    }
    @computed get isLoading() {
        return !(this.hasMetrics && this.hasStudyTypes);
    }

    // metrics
    @action.bound fetchRobSettings() {
        const {assessment_id} = this.config;
        this.resetError();
        fetchRobSettings(
            assessment_id,
            json => {
                this.settings = json;
                this.metrics = json.metrics;
                this.changeSelectedMetric(json.metrics[0].id);
            },
            error => {
                this.setError(error);
            }
        );
    }
    @action.bound changeSelectedMetric(value) {
        this.selectedMetric = value;
        this.selectedScores = [];
    }
    @computed get hasMetrics() {
        return this.selectedMetric !== null;
    }
    @computed get metricChoices() {
        return this.metrics.map(d => {
            return {id: d.id, label: d.name};
        });
    }
    @computed get defaultResponse() {
        return _.first(this.metrics, d => d.id === this.selectedMetric).default_response;
    }

    // filter scores
    @computed get scoreOptions() {
        const metric = _.find(this.metrics, d => d.id == this.selectedMetric);
        return metric.response_values.map(d => {
            return {id: d, label: SCORE_TEXT_DESCRIPTION[d]};
        });
    }
    @action.bound changeSelectedScores(values) {
        this.selectedScores = values;
    }

    // actions: study score responses
    @action.bound fetchScores() {
        this.isFetchingStudyScores = true;
        this.clearFetchedScores();
        const {host, items, assessment_id} = this.config,
            url = h.getUrlWithAssessment(
                h.getObjectUrl(host, items.url, this.selectedMetric) + "scores/",
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

const createStore = function(config) {
    const store = new RobCleanupStore(config);

    autorun(() => {
        // whenever visible scores change, reset selected items
        const newScoreHash = store.visibleStudyScores.map(score => score.id.toString()).join("-");
        if (store.visibleScoreHash !== newScoreHash) {
            store.clearSelectedStudyScores();
            store.setVisibleScoreHash(newScoreHash);
        }
    });

    return store;
};

export default createStore;
