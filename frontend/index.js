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
    utils: {
        DynamicFormset,
        HAWCUtils,
    },
};
