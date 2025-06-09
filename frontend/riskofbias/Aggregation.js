import h from "shared/utils/helpers";

class Aggregation {
    constructor(studies) {
        this.studies = studies;
        this.metrics_dataset = this.build_metrics_dataset();
    }

    build_metrics_dataset() {
        var arr = [];
        this.studies.forEach(function (study) {
            study.riskofbias.forEach(function (domain) {
                domain.criteria.forEach(function (rob) {
                    arr.push(rob);
                });
            });
        });

        var ds = h.groupNest(arr, d => d.data.metric.id);

        var score_binning = function (d) {
            let bins = {};
            d.rob_scores.forEach(rob => {
                if (bins[rob.data.score] === undefined) {
                    bins[rob.data.score] = {
                        rob_scores: [],
                        score: rob.data.score,
                        score_text: rob.data.score_text,
                        score_description: rob.data.score_description,
                    };
                }
                bins[rob.data.score].rob_scores.push(rob);
            });
            return bins;
        };

        ds.forEach(function (v) {
            h.renameProperty(v, "key", "domain");
            h.renameProperty(v, "values", "rob_scores");
            v.domain_text = v.rob_scores[0].data.metric.domain.name;
            v.domain_is_overall_confidence =
                typeof v.rob_scores[0].data.metric.domain.is_overall_confidence === "boolean"
                    ? v.rob_scores[0].data.metric.domain.is_overall_confidence
                    : false;
            v.score_bins = score_binning(v);
        });
        return ds;
    }
}

export default Aggregation;
