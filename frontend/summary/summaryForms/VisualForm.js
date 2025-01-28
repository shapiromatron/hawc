import CrossviewForm from "./CrossviewForm";

class VisualForm {
    static create(visual_type, $el, config) {
        var Cls;
        switch (visual_type) {
            case 1:
                Cls = CrossviewForm;
                break;
            case 0:
            case 4:
            case 5:
            case 6:
            case 7:
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
