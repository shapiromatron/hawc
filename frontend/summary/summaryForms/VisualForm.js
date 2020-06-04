import {EndpointAggregationShim} from "./EndpointAggregationFormReact";
import CrossviewForm from "./CrossviewForm";
import RoBHeatmapForm from "./RoBHeatmapForm";
import RoBBarchartForm from "./RoBBarchartForm";
import ExploratoryHeatmapForm from "./ExploratoryHeatmapForm";

class VisualForm {
    static create(visual_type, $el, config) {
        var Cls;
        switch (visual_type) {
            case 0:
                Cls = EndpointAggregationShim;
                break;
            case 1:
                Cls = CrossviewForm;
                break;
            case 2:
                Cls = RoBHeatmapForm;
                break;
            case 3:
                Cls = RoBBarchartForm;
                break;
            case 4:
            case 5:
                Cls = null;
                break;
            case 6:
                Cls = ExploratoryHeatmapForm;
                break;
            default:
                throw `Error - unknown visualization-type: ${visual_type}`;
        }
        if (Cls) {
            return new Cls($el, config);
        }
    }
}

export default VisualForm;
