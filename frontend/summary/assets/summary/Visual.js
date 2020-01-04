import $ from '$';

import Crossview from './Crossview';
import EndpointAggregation from './EndpointAggregation';
import RoBBarchart from './RoBBarchart';
import RoBHeatmap from './RoBHeatmap';

class Visual {
    static get_object(id, cb) {
        $.get('/summary/api/visual/{0}/'.printf(id), function(d) {
            var Cls;
            switch (d.visual_type) {
                case 'animal bioassay endpoint aggregation':
                    Cls = EndpointAggregation;
                    break;
                case 'animal bioassay endpoint crossview':
                    Cls = Crossview;
                    break;
                case 'risk of bias heatmap':
                case 'study evaluation heatmap':
                    Cls = RoBHeatmap;
                    break;
                case 'risk of bias barchart':
                case 'study evaluation barchart':
                    Cls = RoBBarchart;
                    break;
                default:
                    throw 'Error - unknown visualization-type: {0}'.printf(d.visual_type);
            }
            cb(new Cls(d));
        });
    }

    static displayAsPage(id, $el) {
        $el.html('<p>Loading... <img src="/static/img/loading.gif"></p>');
        Visual.get_object(id, function(d) {
            d.displayAsPage($el);
        });
    }

    static displayAsModal(id, options) {
        Visual.get_object(id, function(d) {
            d.displayAsModal(options);
        });
    }

    static displayInline(id, setTitle, setBody) {
        Visual.get_object(id, (obj) => {
            var title = $('<h4>').html(obj.object_hyperlink()),
                content = $('<div>');

            setTitle(title);
            setBody(content);
            obj.displayAsPage(content, { visualOnly: true });
        });
    }
}

export default Visual;
