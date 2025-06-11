import _ from "lodash";
import {computed, makeObservable} from "mobx";

import {hideScore} from "../constants";
import StudyRobStore from "../stores/StudyRobStore";

class RobDonutStore extends StudyRobStore {
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

    @computed get canShowScoreVisualization() {
        if (this.hasFinalData) {
            // confusing; if all hidden -> don't show; if any not hidden -> show
            return !_.every(this.final.scores.map(d => hideScore(d.score)));
        }
        return true;
    }
}

export default RobDonutStore;
