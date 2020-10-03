import "./utils/startup";

import adminStartup from "./admin";
import animalStartup from "./animal";
import assessmentStartup from "./assessment";
import {nestedTagEditorStartup, smartTagsStartup, textCleanupStartup} from "./assets";
import bmdStartup from "./bmd";
import epiStartup from "./epi";
import epimetaStartup from "./epimeta";
import invitroStartup from "./invitro";
import mgmtStartup from "./mgmt";
import litStartup from "./lit";
import riskofbiasStartup from "./riskofbias";
import studyStartup from "./study";
import {
    summaryStartup,
    summaryFormsStartup,
    dataPivotStartup,
    heatmapTemplateStartup,
    renderPlotlyFromApi,
} from "./summary";
import utils from "./utils";

window.app = {
    adminStartup,
    animalStartup,
    assessmentStartup,
    bmdStartup,
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
    summaryFormsStartup,
    summaryStartup,
    textCleanupStartup,
    utils,
};
