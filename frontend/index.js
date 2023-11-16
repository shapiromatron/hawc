import "./shared/startup";

import {renderPlotlyFigure} from "shared/components/PlotlyFigure";
import renderPlotlyFromApi from "shared/renderPlotlyFromApi";
import DynamicFormset from "shared/utils/DynamicFormset";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

import startup from "./splits";

const getConfig = () => JSON.parse(document.getElementById("config").textContent);

window.app = {
    DynamicFormset,
    HAWCUtils,
    getConfig,
    renderPlotlyFigure,
    renderPlotlyFromApi,
    startup,
    toggleDebug: () => {
        $(".ids").show();
    },
};
