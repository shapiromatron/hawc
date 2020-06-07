import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import HAWCModal from "utils/HAWCModal";
import ExploreHeatmapPlot from "./ExploreHeatmapPlot";
import $ from "$";

class ExploreHeatmap extends BaseVisual {
    constructor(data) {
        super(data);
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>");
        //data = this.getPlotData();

        var data = {};
        data.settings = {
            type: "heatmap",
            plot: {width: undefined, height: undefined}, //svg size, undefined defaults to page content size
            plot_title: "Exploratory heatmap of experiments by species, sex, and health system",
            x_label: "Species & Sex",
            y_label: "Health System",
            x_fields: ["species-name", "animal_group-sex"], //nested fields on x axis
            y_fields: ["endpoint-system"], //nested fields on y axis
            all_fields: [
                "study-short_citation",
                "study-study_identifier",
                "experiment-chemical",
                "animal_group-name",
                "animal_group-sex",
                "species-name",
            ], //all fields we are interested in, ignore excluded fields on detail page
            blacklist_field: "study-short_citation", //additional filter / main identifier

            show_blacklist: true,
            blacklist_width: undefined,
            details_height: undefined,
            color_range: ["white", "green"],
        };
        data.dataset = JSON.parse(
            $.ajax(`/ani/api/assessment/${this.data.assessment}/endpoint-export/?format=json`, {
                async: false,
                dataType: "json",
            }).responseText
        );

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend(title).append(captionDiv);

        new ExploreHeatmapPlot(this, data, options).render($plotDiv);
        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};

        var self = this,
            //data = this.getPlotData(),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal();

        var data = {};
        data.settings = {
            type: "heatmap",
            plot: {width: undefined, height: undefined}, //svg size, undefined defaults to page content size
            plot_title: "Exploratory heatmap of experiments by species, sex, and health system",
            x_label: "Species & Sex",
            y_label: "Health System",
            x_fields: ["species-name", "animal_group-sex"], //nested fields on x axis
            y_fields: ["endpoint-system"], //nested fields on y axis
            all_fields: [
                "study-short_citation",
                "study-study_identifier",
                "experiment-chemical",
                "animal_group-name",
                "animal_group-sex",
                "species-name",
            ], //all fields we are interested in, ignore excluded fields on detail page
            blacklist_field: "study-short_citation", //additional filter / main identifier

            show_blacklist: true,
            blacklist_width: undefined,
            details_height: undefined,
            color_range: ["white", "green"],
        };
        data.dataset = JSON.parse(
            $.ajax(`/ani/api/assessment/${this.data.assessment}/endpoint-export/?format=json`, {
                async: false,
                dataType: "json",
            }).responseText
        );

        modal.getModal().on("shown", function() {
            new ExploreHeatmapPlot(self, data, options).render($plotDiv);
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

export default ExploreHeatmap;
