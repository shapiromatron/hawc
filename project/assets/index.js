// startup
import 'utils/startup';
import utils from 'utils';

// object models
import animal from 'animal';
import assessment from 'assessment';
import dataPivot from 'dataPivot';
import epi from 'epi';
import epimeta from 'epimeta';
import invitro from 'invitro';
import lit from 'lit';
import mgmt from 'mgmt';
import riskofbias from 'riskofbias';
import study from 'study';
import smartTags from 'smartTags';
import summary from 'summary';
import summaryForms from 'summaryForms';

// custom applications
import bmdStartup from 'bmd';
import robVisualStartup from 'robVisual';
import robTableStartup from 'robTable';
import robScoreCleanupStartup from 'robScoreCleanup';
import textCleanupStartup from 'textCleanup';
import nestedTagEditorStartup from 'nestedTagEditor';


window.app = {
    utils,
    animal,
    assessment,
    dataPivot,
    epi,
    epimeta,
    invitro,
    lit,
    mgmt,
    riskofbias,
    study,
    smartTags,
    summary,
    summaryForms,
    bmdStartup,
    robVisualStartup,
    robTableStartup,
    robScoreCleanupStartup,
    textCleanupStartup,
    nestedTagEditorStartup,
};
