import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class MetaProtocol {
    constructor(data) {
        this.data = data;
    }

    static get_detail_url(id) {
        return `/epi-meta/protocol/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/epi-meta/api/protocol/${id}/`, d => cb(new MetaProtocol(d)));
    }

    static displayAsModal(id) {
        MetaProtocol.get_object(id, d => d.displayAsModal());
    }

    static displayFullPager($el, id) {
        MetaProtocol.get_object(id, d => d.displayFullPager($el));
    }

    build_details_table() {
        return new DescriptiveTable()
            .add_tbody_tr("Description", this.data.name)
            .add_tbody_tr("Protocol type", this.data.protocol_type)
            .add_tbody_tr("Literature search strategy", this.data.lit_search_strategy)
            .add_tbody_tr("Literature search start-date", this.data.lit_search_start_date)
            .add_tbody_tr("Literature search end-date", this.data.lit_search_end_date)
            .add_tbody_tr("Literature search notes", this.data.lit_search_notes)
            .add_tbody_tr("Total references from search", this.data.total_references)
            .add_tbody_tr_list("Inclusion criteria", this.data.inclusion_criteria)
            .add_tbody_tr_list("Exclusion criteria", this.data.exclusion_criteria)
            .add_tbody_tr(
                "Total references after inclusion/exclusion",
                this.data.total_studies_identified
            )
            .add_tbody_tr("Additional notes", this.data.notes)
            .get_tbl();
    }

    build_breadcrumbs() {
        var urls = [
            {url: this.data.study.url, name: this.data.study.short_citation},
            {url: this.data.url, name: this.data.name},
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = `<h4>${this.build_breadcrumbs()}</h4>`,
            $content = $('<div class="container-fluid">')
                .append(this.build_details_table())
                .append(this.build_links_div());

        modal.addHeader(title).addBody($content).addFooter("").show({maxWidth: 900});
    }

    displayFullPager($el) {
        $el.hide().append(this.build_details_table()).append(this.build_links_div()).fadeIn();
    }

    build_links_div() {
        var $el = $("<div>"),
            liFunc = d => `<li><a href="${d.url}">${d.label}</a></li>`;

        $el.append("<h3>Results</h3>");
        if (this.data.results.length > 0) {
            $el.append(HAWCUtils.buildUL(this.data.results, liFunc));
        } else {
            $el.append(
                '<p class="form-text text-muted">No results are available for this protocol.</p>'
            );
        }

        return $el;
    }
}

export default MetaProtocol;
