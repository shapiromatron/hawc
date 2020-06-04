import _ from "lodash";
import $ from "$";

import ExploreHeatmap from "summary/summary/ExploreHeatmap";

import BaseVisualForm from "./BaseVisualForm";
import {TextField} from "./Fields";

class ExploratoryHeatmapForm extends BaseVisualForm {
    buildPreview($parent, data) {
        this.preview = new ExploreHeatmap(data).displayAsPage($parent.empty(), {
            dev: true,
        });
    }
    updateSettingsFromPreview() {
        var plotSettings = JSON.stringify(this.preview.data.settings);
        $("#id_settings").val(plotSettings);
        this.unpackSettings();
    }
    afterGetDataHook(data) {}
    initDataForm() {}
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
    ],
});

export default ExploratoryHeatmapForm;
