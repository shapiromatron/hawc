import SmartTagEditor from "shared/smartTags/SmartTagEditor";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

import crossviewStartup from "./crossview";
import exploratoryHeatmapFormAppStartup from "./heatmap";
import prismaFormAppStartup from "./prisma";
import robFormAppStartup from "./rob";

const startup = (config, djangoForm, el) => {
    const startupMapping = {
        1: crossviewStartup,
        2: robFormAppStartup,
        3: robFormAppStartup,
        6: exploratoryHeatmapFormAppStartup,
        9: prismaFormAppStartup,
    };
    const func = startupMapping[config.visual_type];
    if (func) {
        func(el, config, djangoForm);
    }

    $("input[data-pf]").each(HAWCUtils.bindCheckboxToPrefilter);
    new SmartTagEditor($("#id_caption"), {submitEl: "#visualForm", takeFocusEl: "#id_title"});
    if (config.isCreate) {
        $("#id_title").on("keyup", e => $("#id_slug").val(HAWCUtils.urlify(e.target.value)));
    }

    const pdu = document.getElementById("pduDiv");
    if (pdu) {
        // TODO - continue
        console.log(pdu);
        // {% if form.fields.preferred_units %}
        //     window.app.startup("assessmentStartup", function(app){
        //       new app.DoseUnitsWidget($('form'), {
        //         choices: JSON.parse('{{form.fields.preferred_units.choices|safe}}'),
        //         el: '#id_preferred_units',
        //       });
        //     });
        //   {% endif %}
    }
};

export default {
    startup,
};
