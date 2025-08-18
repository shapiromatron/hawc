import $ from "$";
import HAWCUtils from "shared/utils/HAWCUtils";

import Crossview from "./Crossview";
import EndpointAggregation from "./EndpointAggregation";
import ExploreHeatmap from "./ExploreHeatmap";
import ExternalSiteVisual from "./ExternalSiteVisual";
import LiteratureTagtree from "./LiteratureTagtree";
import Prisma from "./Prisma";
import RoBBarchart from "./RoBBarchart";
import RoBHeatmap from "./RoBHeatmap";

class Visual {
    static get_object(id, cb) {
        $.get(`/summary/api/visual/${id}/`, function (d) {
            var Cls;
            switch (d.visual_type) {
                case "animal bioassay endpoint aggregation":
                    Cls = EndpointAggregation;
                    break;
                case "animal bioassay endpoint crossview":
                    Cls = Crossview;
                    break;
                case "risk of bias heatmap":
                case "study evaluation heatmap":
                    Cls = RoBHeatmap;
                    break;
                case "risk of bias barchart":
                case "study evaluation barchart":
                    Cls = RoBBarchart;
                    break;
                case "literature tagtree":
                    Cls = LiteratureTagtree;
                    break;
                case "embedded external website":
                    Cls = ExternalSiteVisual;
                    break;
                case "exploratory heatmap":
                    Cls = ExploreHeatmap;
                    break;
                case "PRISMA":
                    Cls = Prisma;
                    break;
                default:
                    throw `Error - unknown visualization-type: ${d.visual_type}`;
            }
            cb(new Cls(d));
        });
    }

    static displayAsPage(id, $el) {
        $el.html(HAWCUtils.loading());
        Visual.get_object(id, d => d.displayAsPage($el));
    }

    static displayAsModal(id, options) {
        Visual.get_object(id, d => d.displayAsModal(options));
    }

    static displayInline(id, setTitle, setBody) {
        Visual.get_object(id, obj => {
            var title = $("<h4>").html(obj.object_hyperlink()),
                content = $("<div>");

            setTitle(title);
            setBody(content);
            obj.displayAsPage(content, {visualOnly: true});
        });
    }
}

export default Visual;
