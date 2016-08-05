// startup
import 'utils/startup';
import utils from 'utils';

// object models
import animal from 'animal';
import assessment from 'assessment';
import lit from 'lit';
import riskofbias from 'riskofbias';
import study from 'study';

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
    lit,
    riskofbias,
    study,
    bmdStartup,
    robVisualStartup,
    robTableStartup,
    robScoreCleanupStartup,
    textCleanupStartup,
    nestedTagEditorStartup,
};
