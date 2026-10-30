import _ from "lodash";
import {action, computed, makeObservable, observable} from "mobx";

import {fetchRobSettings, fetchRobStudy, fetchStudy} from "../constants";

class StudyRobStore {
    constructor() {
        makeObservable(this);
    }

    @observable settings = null;
    @observable study = null;
    @observable activeRobs = null;

    @computed get domains() {
        return _.keyBy(this.settings.domains, domain => domain.id);
    }

    @computed get metrics() {
        return _.keyBy(this.settings.metrics, metric => metric.id);
    }

    @computed get metricDomains() {
        let {domains} = this;
        return _.chain(this.settings.metrics)
            .map(metric => [metric.id, domains[metric.domain_id]])
            .fromPairs()
            .value();
    }

    @action.bound fetchSettings(assessment_id) {
        return fetchRobSettings(assessment_id, data => {
            this.settings = data;
        }).catch(ex => console.error("Assessment parsing failed", ex));
    }

    @action.bound fetchStudy(study_id) {
        return fetchStudy(study_id, data => {
            this.study = data;
        }).catch(ex => console.error("Study parsing failed", ex));
    }

    @action.bound fetchRobStudy(study_id) {
        return fetchRobStudy(study_id, data => {
            this.activeRobs = data;
        }).catch(ex => console.error("Study parsing failed", ex));
    }

    @action.bound fetchStudyDataAndSettings(study_id, assessment_id) {
        Promise.all([this.fetchStudy(study_id), this.fetchSettings(assessment_id)]);
    }
}

export default StudyRobStore;
