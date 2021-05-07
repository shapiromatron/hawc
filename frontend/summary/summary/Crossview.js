import $ from "$";

import HAWCModal from "utils/HAWCModal";

import SmartTagContainer from "assets/smartTags/SmartTagContainer";

import CrossviewPlot from "./CrossviewPlot";
import EndpointAggregation from "./EndpointAggregation";

class Crossview extends EndpointAggregation {
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

        new CrossviewPlot(this, data, options).render($plotDiv);
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
            new CrossviewPlot(self, data, options).render($plotDiv);
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
            title: this.data.title,
            endpoints: this.endpoints,
            dose_units: this.data.dose_units,
            settings: this.data.settings,
        };
    }
}

export default Crossview;
