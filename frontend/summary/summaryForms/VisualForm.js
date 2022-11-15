import CrossviewForm from "./CrossviewForm";
import {EndpointAggregationShim} from "./EndpointAggregationFormReact";
import RoBBarchartForm from "./RoBBarchartForm";
import RoBHeatmapForm from "./RoBHeatmapForm";

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
            case 6:
                Cls = null;
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
