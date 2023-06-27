import {BEDSettings, BESettings, BSDSettings} from "./bioassay";
import {EcRSettings, EcSDSettings} from "./eco";
import {ERSettings, ESDSettings} from "./epi";

const OPTIONS = {
    "bioassay-study-design": BSDSettings,
    "bioassay-endpoint-summary": BESettings,
    "bioassay-endpoint-doses-summary": BEDSettings,
    "epidemiology-study-design": ESDSettings,
    "epidemiology-result-summary": ERSettings,
    "ecology-study-design": EcSDSettings,
    "ecology-result-summary": EcRSettings,
};

export default OPTIONS;
