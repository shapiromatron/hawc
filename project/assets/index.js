import textCleanupStartup from 'textCleanup';
import robVisualStartup from 'robVisual';
import robTableStartup from 'robTable';
import { renderAggregateGraph } from 'robTable/components/AggregateGraph';
import { renderCrossStudyDisplay } from 'robTable/components/CrossStudyDisplay';
import { renderRiskOfBiasDisplay } from 'robTable/components/RiskOfBiasDisplay';

window.app = {
    textCleanupStartup,
    robVisualStartup,
    robTableStartup,
    renderAggregateGraph,
    renderCrossStudyDisplay,
    renderRiskOfBiasDisplay,
};
