import "./shared/startup";

import DynamicFormset from "shared/utils/DynamicFormset";
import HAWCUtils from "shared/utils/HAWCUtils";
import renderPlotlyFromApi from "shared/renderPlotlyFromApi";
import startup from "./splits";

const getConfig = () => JSON.parse(document.getElementById("config").textContent);

window.app = {
    DynamicFormset,
    HAWCUtils,
    getConfig,
    renderPlotlyFromApi,
    startup,
};
