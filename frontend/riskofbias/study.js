import _ from "lodash";
import h from "shared/utils/helpers";

import RiskOfBiasScore from "./RiskOfBiasScore";
import {SCORE_SHADES, SCORE_TEXT} from "./constants";

/*
Functions designed to transform data from the api to be used in the Study object as well
as RoB heatmaps. Ideally these transforms would be refactored in the future, but for now we
create a standalone functions.
*/

export const mutateRobSettings = settings => {
        // Mutates settings.
        // Build key/map for rob settings
        const domainsMap = _.keyBy(settings.domains, d => d.id),
            metricsMap = _.keyBy(settings.metrics, d => d.id);

        settings.metrics.forEach(metric => {
            metric.domain = domainsMap[metric.domain_id];
        });

        settings.domainsMap = domainsMap;
        settings.metricsMap = metricsMap;
    },
    mutateRobStudies = (studies, rob_settings) => {
        /*
        Mutates array of studies data.
        Nest domain and metrics into risk of bias score objects.
        */
        studies.forEach(study => {
            study.riskofbiases.forEach(robs => {
                robs.scores.forEach(score => {
                    score.metric = rob_settings.metricsMap[score.metric_id];
                    score.study_name = study.short_citation;
                    score.score_description = rob_settings.score_metadata.choices[score.score];
                    score.assessment_id = rob_settings.assessment_id;
                });
            });
            study._robPrepped = true;
        });
    },
    transformStudy = function (study, data) {
        // unpack rob information and nest by domain
        mutateRobSettings(data.rob_settings);
        mutateRobStudies([data], data.rob_settings);

        let final = _.find(data.riskofbiases, {final: true, active: true}),
            riskofbias = [];

        if (final && final.scores) {
            // build scores
            riskofbias = final.scores.map(score => {
                score.score_color = SCORE_SHADES[score.score];
                score.score_text_color = h.contrastingColor(score.score_color);
                score.score_text = SCORE_TEXT[score.score];
                return new RiskOfBiasScore(study, score);
            });

            // group rob by domains
            riskofbias = h.groupNest(riskofbias, d => d.data.metric.domain.name);

            // now generate a score for each domain (aggregating metrics)
            riskofbias.forEach(rob => {
                rob.domain = rob.values[0].data.metric.domain.id;
                rob.domain_text = rob.values[0].data.metric.domain.name;
                rob.domain_is_overall_confidence =
                    typeof rob.values[0].data.metric.domain.is_overall_confidence === "boolean"
                        ? rob.values[0].data.metric.domain.is_overall_confidence
                        : false;
                rob.criteria = rob.values;
            });
        }

        return {final, riskofbias};
    };
