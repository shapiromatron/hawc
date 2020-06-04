import _ from "lodash";
import $ from "$";

import ExploreHeatmap from "summary/summary/ExploreHeatmap";

import BaseVisualForm from "./BaseVisualForm";
import {TextField} from "./Fields";

class ExploratoryHeatmapForm extends BaseVisualForm {
    constructor(data) {
        super(...arguments);
        this.heatmap = null;
        this.heatmapDataset = null;
    }

    buildPreview($parent, data) {
        if (this.heatmap === null) {
            this.heatmap = new ExploreHeatmap(data);
        } else {
            this.heatmap.data = data;
        }
        this.heatmap.dataset = this.heatmapDataset;
        this.preview = this.heatmap.displayAsPage($parent.empty(), {
            dev: true,
        });
        this.heatmapDataset = this.heatmap.dataset;
    }
    updateSettingsFromPreview() {
        var plotSettings = JSON.stringify(this.preview.data.settings);
        $("#id_settings").val(plotSettings);
        this.unpackSettings();
    }
    afterSettingsSetup() {
        const requireNewDataFetch = () => {
            this.heatmapDataset = null;
        };
        $('#settings_overall input[name="title"]').change(requireNewDataFetch);
    }
}

_.extend(ExploratoryHeatmapForm, {
    tabs: [{name: "overall", label: "General settings"}],
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "Title",
            tab: "overall",
        },
        {
            type: TextField,
            name: "x_label",
            label: "X label",
            def: "",
            tab: "overall",
        },
        {
            type: TextField,
            name: "y_label",
            label: "Y label",
            def: "",
            tab: "overall",
        },
    ],
});

export default ExploratoryHeatmapForm;
