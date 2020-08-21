import DoseUnitsWidget from "./DoseUnitsWidget";
import renderDssToxTabs from "./DssToxTabs";

const assessmentStartup = {
    DoseUnitsWidget,
    renderDssToxTabs,
};

window.app.assessmentStartup = assessmentStartup;

export default assessmentStartup;
