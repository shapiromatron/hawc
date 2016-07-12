import { renderCrossStudyDisplay } from 'robTable/components/CrossStudyDisplay';
import { renderRiskOfBiasDisplay } from 'robTable/components/RiskOfBiasDisplay';
import { renderStudyDisplay } from 'robTable/components/StudyDisplay';
import robScoreCleanupStartup from 'robScoreCleanup';
import robTableStartup from 'robTable';
import robVisualStartup from 'robVisual';
import textCleanupStartup from 'textCleanup';

window.app = {
    renderCrossStudyDisplay,
    renderRiskOfBiasDisplay,
    renderStudyDisplay,
    robScoreCleanupStartup,
    robTableStartup,
    robVisualStartup,
    textCleanupStartup,
};
