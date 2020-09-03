import "../utils/startup";

import adminStartup from "../admin";
import animalStartup from "../animal";
import assessmentStartup from "../assessment";
import {nestedTagEditorStartup, smartTagsStartup, textCleanupStartup} from "../assets";
import bmdStartup from "../bmd";
import epiStartup from "../epi";
import epimetaStartup from "../epimeta";
import invitroStartup from "../invitro";
import mgmtStartup from "../mgmt";
import litStartup from "../lit";
import riskofbiasStartup from "../riskofbias";
import studyStartup from "../study";
import utils from "../utils";

window.app = {
    adminStartup,
    animalStartup,
    assessmentStartup,
    bmdStartup,
    epiStartup,
    epimetaStartup,
    invitroStartup,
    litStartup,
    mgmtStartup,
    nestedTagEditorStartup,
    riskofbiasStartup,
    smartTagsStartup,
    studyStartup,
    textCleanupStartup,
    utils,
};
