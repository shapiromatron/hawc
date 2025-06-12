import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

import RoBBarchartPlot from "./RoBBarchartPlot";
import RoBHeatmap from "./RoBHeatmap";
import {addLabelIndicators} from "./common";

class RoBBarchart extends RoBHeatmap {
    displayAsPage($el, options) {
        var title = $("<h2>").text(this.data.title),
            labelIndicators = addLabelIndicators(this.data.label_indicators_htmx),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            data = this.getPlotData();

        options = options || {};

        const actions = window.isEditable ? this.addActionsMenu() : null;

        $el.empty().append($plotDiv);

        if (!options.visualOnly) {
            var headerRow = $('<div class="d-flex">').append([
                title,
                labelIndicators,
                HAWCUtils.unpublished(this.data.published, window.isEditable),
                actions,
            ]);
            $el.prepend(headerRow).append(captionDiv);
        }

        new RoBBarchartPlot(this, data, options).render($plotDiv);
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

        modal.getModal().on("shown.bs.modal", function () {
            new RoBBarchartPlot(self, data, options).render($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader([
                $("<h4>").text(this.data.title),
                HAWCUtils.unpublished(this.data.published, window.isEditable),
            ])
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }

    displayAsPreview(el, options) {
        const data = this.getPlotData();
        return new RoBBarchartPlot(this, data, options).render($(el));
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

export default RoBBarchart;
