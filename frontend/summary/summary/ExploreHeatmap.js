import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import HAWCModal from "utils/HAWCModal";
import ExploreHeatmapPlot from "./ExploreHeatmapPlot";
import $ from "$";

class ExploreHeatmap extends BaseVisual {
    constructor(data, dataset) {
        super(data);
        this.dataset = dataset || null;
    }

    getSettings() {
        const {settings} = this.data;
        return {
            type: "heatmap",
            plot: {width: undefined, height: undefined}, //svg size, undefined defaults to page content size
            plot_title: settings.title,
            x_label: settings.x_label,
            y_label: settings.y_label,
            title: settings.title,
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
    }

    clearDataset() {
        this.dataset = null;
    }

    getDataset(url) {
        if (!this.dataset) {
            this.dataset = JSON.parse(
                $.ajax(url, {
                    async: false,
                    dataType: "json",
                }).responseText
            );
        }
        return this.dataset;
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            data = {
                settings: this.getSettings(),
                dataset: this.getDataset(
                    `/ani/api/assessment/${this.data.assessment}/endpoint-export/?format=json`
                ),
            };
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
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal(),
            data = {
                settings: this.getSettings(),
                dataset: this.getDataset(
                    `/ani/api/assessment/${this.data.assessment}/endpoint-export/?format=json`
                ),
            };

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
}

export default ExploreHeatmap;
