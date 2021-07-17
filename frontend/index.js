import "./utils/startup";

import assessmentStartup from "./assessment";
import {nestedTagEditorStartup, smartTagsStartup, textCleanupStartup} from "./assets";
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
import utils from "./utils";
import startup from "./splits";

const getConfig = () => JSON.parse(document.getElementById("config").textContent);

window.app = {
    getConfig,
    startup,
    assessmentStartup,
    dataPivotStartup,
    heatmapTemplateStartup,
    nestedTagEditorStartup,
    renderPlotlyFromApi,
    smartTagsStartup,
    summaryStartup,
    summaryFormsStartup,
    summaryTableViewStartup,
    summaryTableEditStartup,
    summaryTextStartup,
    textCleanupStartup,
    utils,
};
