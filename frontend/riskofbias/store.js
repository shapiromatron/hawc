import _ from "lodash";
import {observable, computed, action} from "mobx";

import {BIAS_DIRECTION_SIMPLE} from "riskofbias/constants";
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

    @computed get shouldUse() {
        return this.study.assessment.enable_risk_of_bias && this.final;
    }

    @computed get domains() {
        return this.settings.domains.reduce(function(obj, d) {
            obj[d.id] = d;
            return obj;
        }, {});
    }

    @computed get metrics() {
        return this.settings.metrics.reduce(function(obj, m) {
            obj[m.id] = m;
            return obj;
        }, {});
    }

    @computed get metricDomains() {
        let {domains, metrics} = this;
        return this.settings.metrics.reduce(function(obj, m) {
            obj[m.id] = domains[metrics[m.id].domain_id];
            return obj;
        }, {});
    }

    getMultiScoreDisplaySettings(scores) {
        // Return visualization/color settings for situations where multiple scores may exist for
        // a given metric (eg, study-level override settings).
        // By default, if multiple scores exist and show he defaults score label if one exists.
        // If the default score does not exist, present the value of the first score (random).
        let sortedScores = _.orderBy(scores, "score", "desc"),
            defaultScore = _.find(scores, {is_default: true}) || sortedScores[0],
            shades = _.chain(sortedScores)
                .map(score => this.settings.score_metadata.colors[score.score])
                .uniq()
                .value(),
            symbols = _.chain(sortedScores)
                .map(score => this.settings.score_metadata.symbols[score.score])
                .uniq()
                .value(),
            symbolText = symbols.join(" / "),
            symbolShortText =
                symbols.length === 1
                    ? symbols[0]
                    : `${this.settings.score_metadata.symbols[defaultScore.score]}✱`,
            directions = _.chain(sortedScores)
                .map(score => score.bias_direction)
                .uniq()
                .value(),
            directionText = _.chain(directions)
                .map(d => BIAS_DIRECTION_SIMPLE[d])
                .value()
                .join(""),
            reactStyle,
            svgStyle,
            cssStyle;

        if (shades.length == 1) {
            reactStyle = {backgroundColor: shades[0]};
            cssStyle = {"background-color": shades[0]};
            svgStyle = {fill: shades[0]};
        } else if (shades.length >= 2) {
            let dim = Math.ceil(50 / shades.length),
                reactGradients = shades
                    .map((shade, idx) => `${shade} ${idx * dim}px, ${shade} ${(idx + 1) * dim}px`)
                    .join(", "),
                svgShades = shades
                    .map((shade, idx) => {
                        const offset1 = Math.ceil((idx / shades.length) * 100),
                            offset2 = Math.ceil(((idx + 1) / shades.length) * 100);
                        return `<stop offset="${offset1}%" stop-color="${shade}" stop-opacity="1" />
                                <stop offset="${offset2}%" stop-color="${shade}" stop-opacity="1" />`;
                    })
                    .join(""),
                gradientId = `gradient${scores[0].id}`,
                gradient = `<linearGradient id="${gradientId}" x1="0" y1="0" x2="25%" y2="25%" spreadMethod="repeat">${svgShades}</linearGradient>`;

            reactStyle = {background: `repeating-linear-gradient(-45deg, ${reactGradients})`};
            cssStyle = reactStyle;
            svgStyle = {
                gradient,
                fill: `url(#${gradientId})`,
            };
        }

        return {
            reactStyle,
            cssStyle,
            symbols,
            symbolText,
            symbolShortText,
            directions,
            directionText,
            svgStyle,
        };
    }

    // computed props
    @action.bound fetchSettings(assessment_id) {
        const url = `/rob/api/assessment/${assessment_id}/settings/`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.settings = data;
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }

    @action.bound fetchStudy(study_id) {
        const url = `/study/api/study/${study_id}/v2/`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.study = data;
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
}

const store = new StudyRobStore();

// singleton pattern
export default store;
