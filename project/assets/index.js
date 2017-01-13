// startup
import 'utils/startup';
import utils from 'utils';

// object models
import animalStartup from 'animal/split';
import assessmentStartup from 'assessment/split';
import dataPivotStartup from 'dataPivot/split';
import epiStartup from 'epi/split';
import epimetaStartup from 'epimeta/split';
import invitroStartup from 'invitro/split';
import litStartup from 'lit/split';
import mgmtStartup from 'mgmt/split';
import riskofbiasStartup from 'riskofbias/split';
import studyStartup from 'study/split';
import smartTagsStartup from 'smartTags/split';
import summaryStartup from 'summary/split';
import summaryFormsStartup from 'summaryForms/split';

// custom applications
import bmdStartup from 'bmd';
import robVisualStartup from 'robVisual';
import robTableStartup from 'robTable';
import robScoreCleanupStartup from 'robScoreCleanup';
import textCleanupStartup from 'textCleanup';
import nestedTagEditorStartup from 'nestedTagEditor';


window.app = {
    utils,
    animalStartup,
    assessmentStartup,
    dataPivotStartup,
    epiStartup,
    epimetaStartup,
    invitroStartup,
    litStartup,
    mgmtStartup,
    riskofbiasStartup,
    studyStartup,
    smartTagsStartup,
    summaryStartup,
    summaryFormsStartup,
    bmdStartup,
    robVisualStartup,
    robTableStartup,
    robScoreCleanupStartup,
    textCleanupStartup,
    nestedTagEditorStartup,
};
