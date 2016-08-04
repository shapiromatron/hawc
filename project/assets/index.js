import robScoreCleanupStartup from 'robScoreCleanup';
import robTableStartup from 'robTable';
import robVisualStartup from 'robVisual';
import textCleanupStartup from 'textCleanup';
import bmdStartup from 'bmd';
import { BMDLine } from 'bmd/models/model.js';

import { renderCrossStudyDisplay } from 'robTable/components/CrossStudyDisplay';
import { renderRiskOfBiasDisplay } from 'robTable/components/RiskOfBiasDisplay';
import { renderStudyDisplay } from 'robTable/components/StudyDisplay';
import nestedTagEditorStartup from 'nestedTagEditor';

import assessment from 'assessment';
import animal from 'animal';
import lit from 'lit';
import study from 'study';
import riskofbias from 'riskofbias';


window.app = {
    renderCrossStudyDisplay,
    renderRiskOfBiasDisplay,
    renderStudyDisplay,
    robScoreCleanupStartup,
    robTableStartup,
    robVisualStartup,
    textCleanupStartup,
    bmdStartup,
    BMDLine,
    nestedTagEditorStartup,
    assessment,
    animal,
    lit,
    study,
    riskofbias,
};
