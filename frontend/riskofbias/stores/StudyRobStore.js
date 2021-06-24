import _ from "lodash";
import {observable, computed, action, toJS} from "mobx";

import {robSettingsUrl, robStudyUrl, hideScore} from "../constants";
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

    @computed get canShowScoreVisualization() {
        if (this.hasFinalData) {
            // confusing; if all hidden -> don't show; if any not hidden -> show
            return !_.every(this.final.scores.map(d => hideScore(d.score)));
        }
        return true;
    }

    @computed get metricDomains() {
        let {domains} = this;
        return _.chain(this.settings.metrics)
            .map(metric => [metric.id, domains[metric.domain_id]])
            .fromPairs()
            .value();
    }

    @action.bound fetchSettings(assessment_id) {
        const url = robSettingsUrl(assessment_id);
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.settings = data;
            })
            .catch(ex => console.error("Assessment parsing failed", ex));
    }

    @action.bound fetchStudy(study_id) {
        const url = robStudyUrl(study_id);
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.study = data;
            })
            .catch(ex => console.error("Study parsing failed", ex));
    }

    @action.bound fetchStudyDataAndSettings(study_id, assessment_id) {
        Promise.all([this.fetchStudy(study_id), this.fetchSettings(assessment_id)]);
    }
}

export default StudyRobStore;
