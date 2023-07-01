import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class DataExtraction {
    constructor(data) {
        this.data = data;
    }

    static get_detail_url(id) {
        return `/epidemiology/design/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/epidemiology/api/data-extraction/${id}/`, d => cb(new DataExtraction(d)));
    }

    static displayAsModal(id) {
        DataExtraction.get_object(id, d => d.displayAsModal());
    }

    build_details_table() {
        return new DescriptiveTable().add_tbody_tr("HERE", "THERE").get_tbl();
    }

    build_breadcrumbs() {
        var urls = [{url: `/epidemiology/design/${this.data.design}/`, name: "Design"}];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = `<h4>${this.build_breadcrumbs()}</h4>`,
            $content = $('<div class="container-fluid">').append(this.build_details_table());

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
}

export {DataExtraction};
