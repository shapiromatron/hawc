import _ from "lodash";
import Aggregation from "riskofbias/Aggregation";
import {mutateRobSettings, mutateRobStudies} from "riskofbias/study";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import Study from "study/Study";

import $ from "$";

import BaseVisual from "./BaseVisual";
import RoBHeatmapPlot from "./RoBHeatmapPlot";

class RoBHeatmap extends BaseVisual {
    static transformData(data) {
        mutateRobSettings(data.rob_settings);
        mutateRobStudies(data.studies, data.rob_settings);
    }

    constructor(data) {
        super(data);
        RoBHeatmap.transformData(data);
        var studies = _.map(data.studies, d => new Study(d));
        this.roba = new Aggregation(studies);
        delete this.data.studies;
    }

    displayAsPage($el, options) {
        var title = $("<h2>").text(this.data.title),
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
            rob_settings: this.data.rob_settings,
        };
    }
}

export default RoBHeatmap;
