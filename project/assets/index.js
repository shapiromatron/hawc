import textCleanupStartup from 'textCleanup';
import robVisualStartup from 'robVisual';
import robTableStartup from 'robTable';
import { renderCrossStudyDisplay } from 'robTable/components/CrossStudyDisplay';
import { renderRiskOfBiasDisplay } from 'robTable/components/RiskOfBiasDisplay';
import { renderStudyDisplay } from 'robTable/components/StudyDisplay';
import nestedTagEditorStartup from 'nestedTagEditor';

window.app = {
    textCleanupStartup,
    robVisualStartup,
    robTableStartup,
    renderCrossStudyDisplay,
    renderRiskOfBiasDisplay,
    renderStudyDisplay,
    nestedTagEditorStartup,
};
