import {BSDSettings, BESettings, BEDSettings} from "./bioassay";
import {ESDSettings, ERSettings} from "./epi";
import {RobSettings} from "./rob";

const OPTIONS = {
    "bioassay-study-design": BSDSettings,
    "bioassay-endpoint-summary": BESettings,
    "bioassay-endpoint-doses-summary": BEDSettings,
    "epidemiology-study-design": ESDSettings,
    "epidemiology-result-summary": ERSettings,
    "rob-study": RobSettings,
};

export default OPTIONS;
