import _ from "lodash";
import h from "shared/utils/helpers";

class RiskOfBiasScore {
    constructor(study, data) {
        this.study = study;
        this.data = data;
    }

    static format_for_react(robs, config) {
        config = config || {display: "final", isForm: false};
        var scores = robs.map(rob => {
            if (!rob.data.author) {
                _.extend(rob.data, {author: {full_name: ""}});
            }
            if (rob.study) {
                _.extend(rob.data, {
                    study: {
                        name: rob.study.data.short_citation,
                        url: rob.study.data.url,
                    },
                });
            }
            return _.extend(rob.data, {
                domain: rob.data.metric.domain.id,
                domain_name: rob.data.metric.domain.name,
                final: true,
            });
        });

        return {
            domain: robs[0].data.metric.domain.name,
            metric: robs[0].data.metric,
            scores: h.groupNest(
                scores,
                d => d.metric.domain.name,
                d => d.metric.name
            ),
            config,
        };
    }
}

export default RiskOfBiasScore;
