import _ from "lodash";
import {observable, computed, action} from "mobx";

import {fetchRobSettings, fetchRobStudy} from "../constants";
import h from "shared/utils/helpers";

class StudyRobStore {
    @observable settings = null;
    @observable study = null;

    @computed get final() {
        return _.find(this.study.riskofbiases, {
            final: true,
            active: true,
        });
    }

    @computed get hasLoaded() {
        return _.isObject(this.settings) && _.isObject(this.study);
    }

    @computed get hasFinalData() {
        return this.hasLoaded && this.study.assessment.enable_risk_of_bias && this.final;
    }

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
        return fetchRobStudy(study_id, data => {
            this.study = data;
        }).catch(ex => console.error("Study parsing failed", ex));
    }

    @action.bound fetchStudyDataAndSettings(study_id, assessment_id) {
        Promise.all([this.fetchStudy(study_id), this.fetchSettings(assessment_id)]);
    }
}

export default StudyRobStore;
