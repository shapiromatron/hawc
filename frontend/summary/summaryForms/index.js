import $ from "$";
import SmartTagEditor from "shared/smartTags/SmartTagEditor";
import HAWCUtils from "shared/utils/HAWCUtils";

import renderPreferredUnits from "../dataPivot/components/PreferredUnits";
import crossviewStartup from "./crossview";
import exploratoryHeatmapFormAppStartup from "./heatmap";
import prismaFormAppStartup from "./prisma";
import robFormAppStartup from "./rob";

const appStartupMapping = {
    1: crossviewStartup,
    2: robFormAppStartup,
    3: robFormAppStartup,
    6: exploratoryHeatmapFormAppStartup,
    9: prismaFormAppStartup,
};

const startup = (config, djangoForm, el) => {
    // startup application
    const func = appStartupMapping[config.visual_type];
    if (func) {
        func(el, config, djangoForm);
    }

    // connect prefilters
    $("input[data-pf]").each(HAWCUtils.bindCheckboxToPrefilter);

    // enable Quill for captoin
    new SmartTagEditor($("#id_caption"), {submitEl: "#visualForm", takeFocusEl: "#id_title"});

    // make title update the slug value (create only)
    if (config.isCreate) {
        $("#id_title").on("keyup", e => $("#id_slug").val(HAWCUtils.urlify(e.target.value)));
    }

    // enabled preferred units widget
    if (config.preferred_units) {
        renderPreferredUnits(document.getElementById("id_preferred_units"), config);
    }
};

export default {
    startup,
};
