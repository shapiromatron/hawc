import $ from "$";
import _ from "lodash";

import HAWCModal from "utils/HAWCModal";
import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import Study from "study/Study";
import Aggregation from "riskofbias/Aggregation";

import RoBHeatmapPlot from "./RoBHeatmapPlot";
import BaseVisual from "./BaseVisual";

const prepareRobScores = data => {
    /*
    Filter riskofbias scores to only show active/final ones. Nest domain and metrics into
    risk of bias score objects.
    */
    const domains = _.keyBy(data.rob_settings.domains, d => d.id),
        metrics = _.keyBy(data.rob_settings.metrics, d => d.id);

    data.rob_settings.metrics.forEach(metric => {
        metric.domain = domains[metric.domain_id];
    });

    data.studies.forEach(study => {
        study.riskofbiases = study.riskofbiases.filter(d => d.final && d.active);
        study.riskofbiases.forEach(robs => {
            robs.scores.forEach(score => {
                score.metric = metrics[score.metric_id];
                score.score_description = data.rob_settings.score_metadata.choices[score.score];
                score.assessment_id = data.rob_settings.assessment_id;
            });
        });
    });
};

class RoBHeatmap extends BaseVisual {
    constructor(data) {
        super(data);
        prepareRobScores(data);
        var studies = _.map(data.studies, d => new Study(d));
        this.roba = new Aggregation(studies);
        delete this.data.studies;
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            data = this.getPlotData();

        options = options || {};

        const actions = window.isEditable ? this.addActionsMenu() : null;

        $el.empty().append($plotDiv);

        if (!options.visualOnly) {
            $el.prepend([actions, title]).append(captionDiv);
        }

        new RoBHeatmapPlot(this, data, options).render($plotDiv);
        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};

        var self = this,
            data = this.getPlotData(),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal();

        modal.getModal().on("shown.bs.modal", function() {
            new RoBHeatmapPlot(self, data, options).render($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader($("<h4>").text(this.data.title))
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }

    getPlotData() {
        return {
            aggregation: this.roba,
            settings: this.data.settings,
            assessment_rob_name: this.data.assessment_rob_name,
        };
    }
}

export default RoBHeatmap;
