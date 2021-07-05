import "./shared/startup";

import adminStartup from "./admin";
import animalStartup from "./animal";
import assessmentStartup from "./assessment";
import {bmds2Startup, bmds3Startup} from "./bmd";
import epiStartup from "./epi";
import epimetaStartup from "./epimeta";
import invitroStartup from "./invitro";
import mgmtStartup from "./mgmt";
import litStartup from "./lit";
import riskofbiasStartup from "./riskofbias";
import studyStartup from "./study";
import {
    DynamicFormset,
    HAWCUtils,
    nestedTagEditorStartup,
    smartTagsStartup,
    textCleanupStartup,
} from "./shared";
import {
    summaryStartup,
    summaryFormsStartup,
    summaryTextStartup,
    dataPivotStartup,
    heatmapTemplateStartup,
    renderPlotlyFromApi,
    summaryTableViewStartup,
    summaryTableEditStartup,
} from "./summary";

window.app = {
    adminStartup,
    animalStartup,
    assessmentStartup,
    bmds2Startup,
    bmds3Startup,
    dataPivotStartup,
    epiStartup,
    epimetaStartup,
    heatmapTemplateStartup,
    invitroStartup,
    litStartup,
    mgmtStartup,
    nestedTagEditorStartup,
    renderPlotlyFromApi,
    riskofbiasStartup,
    smartTagsStartup,
    studyStartup,
    summaryStartup,
    summaryFormsStartup,
    summaryTableViewStartup,
    summaryTableEditStartup,
    summaryTextStartup,
    textCleanupStartup,
    utils: {
        DynamicFormset,
        HAWCUtils,
    },
};
