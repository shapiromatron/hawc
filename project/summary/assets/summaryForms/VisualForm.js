import { EndpointAggregationShim } from './EndpointAggregationFormReact';
import CrossviewForm from './CrossviewForm';
import RoBHeatmapForm from './RoBHeatmapForm';
import RoBBarchartForm from './RoBBarchartForm';

class VisualForm {
    static create(visual_type, $el) {
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
            default:
                throw 'Error - unknown visualization-type: {0}'.printf(visual_type);
        }
        return new Cls($el);
    }
}

export default VisualForm;
