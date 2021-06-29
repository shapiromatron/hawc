import _ from "lodash";

/*
Functions designed to transform data from the api to be used in the Study object as well
as RoB heatmaps. Ideally these transforms would be refactored in the future, but for now we
create a standalone functions.
*/

export const transformRobSettings = settings => {
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
    transformRobStudies = (studies, rob_settings) => {
        /*
        Mutates array of studies data.
        Nest domain and metrics into risk of bias score objects.
        */
        studies.forEach(study => {
            study.riskofbiases.forEach(robs => {
                robs.scores.forEach(score => {
                    score.metric = rob_settings.metricsMap[score.metric_id];
                    score.score_description = rob_settings.score_metadata.choices[score.score];
                    score.assessment_id = rob_settings.assessment_id;
                });
            });
            study._robPrepped = true;
        });
    };
