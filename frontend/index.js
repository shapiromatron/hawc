import "./shared/startup";

import assessmentStartup from "./assessment";
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
import startup from "./splits";

const getConfig = () => JSON.parse(document.getElementById("config").textContent);

window.app = {
    DynamicFormset,
    HAWCUtils,
    assessmentStartup,
    dataPivotStartup,
    getConfig,
    heatmapTemplateStartup,
    nestedTagEditorStartup,
    renderPlotlyFromApi,
    smartTagsStartup,
    startup,
    summaryFormsStartup,
    summaryStartup,
    summaryTableEditStartup,
    summaryTableViewStartup,
    summaryTextStartup,
    textCleanupStartup,
};
