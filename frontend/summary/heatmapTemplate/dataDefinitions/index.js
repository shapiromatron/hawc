import {BEDSettings, BESettings, BSDSettings} from "./bioassay";
import {ERSettings, ESDSettings} from "./epi";
import {ERv2Settings, ESDv2Settings} from "./epiv2";

const OPTIONS = {
    "bioassay-study-design": BSDSettings,
    "bioassay-endpoint-summary": BESettings,
    "bioassay-endpoint-doses-summary": BEDSettings,
    "epidemiology-study-design": ESDSettings,
    "epidemiology-result-summary": ERSettings,
    "epidemiology-v2-study-design": ESDv2Settings,
    "epidemiology-v2-result-summary": ERv2Settings,
};

export default OPTIONS;
