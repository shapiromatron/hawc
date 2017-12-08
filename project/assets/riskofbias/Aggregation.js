import d3 from 'd3';


class Aggregation {

    constructor(studies){
        this.studies = studies;
        this.metrics_dataset = this.build_metrics_dataset();
    }

    build_metrics_dataset(){
        var arr = [];
        this.studies.forEach(function(study){
            study.riskofbias.forEach(function(domain){
                domain.criteria.forEach(function(rob){
                    arr.push(rob);
                });
            });
        });

        var ds = d3.nest()
                    .key(function(d){return d.data.metric.id;})
                    .entries(arr);

        var score_binning = function(d){
            var score_bins = {
                '0': {rob_scores: [], score: 0, score_text: 'N/A', score_description: 'Not applicable'},
                '1': {rob_scores: [], score: 1, score_text: '--', score_description: 'Critically deficient'},
                '2': {rob_scores: [], score: 2, score_text: '-', score_description: 'Poor'},
                '3': {rob_scores: [], score: 3, score_text: '+', score_description: 'Adequate'},
                '4': {rob_scores: [], score: 4, score_text: '++', score_description: 'Good'},
                '10': {rob_scores: [], score: 10, score_text: 'NR', score_description: 'Not reported'},
            };
            d.rob_scores.forEach(function(rob){
                score_bins[rob.data.score].rob_scores.push(rob);
            });
            return score_bins;
        };

        ds.forEach(function(v){
            v.rename_property('key', 'domain');
            v.rename_property('values', 'rob_scores');
            v.domain_text = v.rob_scores[0].data.metric.domain.name;
            v.domain_is_overall_confidence = (typeof(v.rob_scores[0].data.metric.domain.is_overall_confidence) === "boolean") ? v.rob_scores[0].data.metric.domain.is_overall_confidence : false;
            var possible_score = d3.sum(v.rob_scores.map(function(v){return (v.data.score>0)?4:0;})),
                score = d3.sum(v.rob_scores.map(function(v){return v.data.score;}));
            v.score = (possible_score>0)?d3.round(score/possible_score*100, 2):0;
            v.score_bins = score_binning(v);
        });

        return ds;
    }

}


export default Aggregation;
