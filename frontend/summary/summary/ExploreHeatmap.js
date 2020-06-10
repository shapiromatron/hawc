import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import HAWCModal from "utils/HAWCModal";
import ExploreHeatmapPlot from "./ExploreHeatmapPlot";
import $ from "$";

import h from "shared/utils/helpers";
import {NULL_VALUE} from "./constants";

class ExploreHeatmap extends BaseVisual {
    constructor(data, dataset) {
        super(data);
        this.dataset = dataset || null;
    }

    getSettings() {
        const {settings} = this.data;
        return {
            type: "heatmap",
            plot_title: settings.title,
            x_label: settings.x_label,
            y_label: settings.y_label,
            x_fields: settings.x_fields.filter(d => d.column !== NULL_VALUE).map(d => d.column),
            y_fields: settings.y_fields.filter(d => d.column !== NULL_VALUE).map(d => d.column),
            x_fields_new: settings.x_fields.filter(d => d.column !== NULL_VALUE),
            y_fields_new: settings.y_fields.filter(d => d.column !== NULL_VALUE),
            table_fields: settings.table_fields,
            filter_widgets: settings.filter_widgets,
            blacklist_field: "study-short_citation", //additional filter / main identifier
            color_range: ["white", "black"],
        };
    }

    getDataset(callback) {
        const url = this.data.settings.data_url;
        if (this.dataset) {
            callback({dataset: this.dataset});
        } else {
            fetch(url, h.fetchGet)
                .then(response => response.json())
                .then(json => {
                    this.dataset = json;
                    return {dataset: json};
                })
                .catch(error => {
                    callback({error});
                })
                .then(callback);
        }
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            callback = resp => {
                if (window.isEditable) {
                    title.append(this.addActionsMenu());
                }
                if (resp.dataset) {
                    const data = {
                        settings: this.getSettings(),
                        dataset: resp.dataset,
                    };

                    $el.empty().append($plotDiv);
                    if (!options.visualOnly) {
                        $el.prepend(title).append(captionDiv);
                    }

                    new ExploreHeatmapPlot(this, data, options).render($plotDiv);

                    caption.renderAndEnable();
                } else if (resp.error) {
                    $el.empty()
                        .prepend(title)
                        .append(this.getErrorDiv());
                } else {
                    throw "Unknown status.";
                }
            };

        options = options || {};
        this.getDataset(callback);
    }

    displayAsModal(options) {
        options = options || {};

        var self = this,
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal(),
            callback = resp => {
                if (resp.error) {
                    const data = {
                        settings: this.getSettings(),
                        dataset: resp.dataset,
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
                } else if (resp.error) {
                    modal
                        .addHeader($("<h4>").text(this.data.title))
                        .addBody(this.getErrorDiv())
                        .addFooter("")
                        .show({maxWidth: 1200});
                } else {
                    throw "Unknown status.";
                }
            };

        options = options || {};
        this.getDataset(callback);
    }

    getErrorDiv() {
        return `<div class="alert alert-danger" role="alert">
            <i class="fa fa-exclamation-circle"></i>&nbsp;An error occurred; please modify settings...
        </div>`;
    }
}

export default ExploreHeatmap;
