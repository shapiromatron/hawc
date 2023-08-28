import _ from "lodash";
import RiskOfBiasScore from "riskofbias/RiskOfBiasScore";
import {renderStudyDisplay} from "riskofbias/robTable/components/StudyDisplay";
import {transformStudy} from "riskofbias/study";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import Hero from "shared/utils/Hero";
import {getReferenceTagListUrl} from "shared/utils/urls";

import $ from "$";

class Study {
    constructor(data) {
        this.data = data;
        if (this.data.assessment.enable_risk_of_bias) {
            _.extend(this, transformStudy(this, data));
        }
    }

    static get_detail_url(id) {
        return `/study/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/study/api/study/${id}/`, d => cb(new Study(d)));
    }

    static displayAsModal(id) {
        Study.get_object(id, d => d.displayAsModal());
    }

    static render(id, $div, $shower) {
        Study.get_object(id, d => d.render($div, $shower));
    }

    static displayInline(id, setTitle, setBody) {
        Study.get_object(id, obj => {
            var title = $(`<h4><b>${obj.build_breadcrumbs()}</b></h4>`),
                content = $("<div>");

            setTitle(title);
            setBody(content);
            obj.render(content);
        });
    }

    has_riskofbias() {
        return this.riskofbias && this.riskofbias.length > 0;
    }

    build_breadcrumbs() {
        var urls = [{url: this.data.url, name: this.data.short_citation}];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_name() {
        return this.data.short_citation;
    }

    get_url() {
        return `<a href="${this.data.url}">${this.data.short_citation}</a>`;
    }

    _get_data_types() {
        return _.chain(Study.typeNames)
            .keys()
            .filter(d => this.data[d])
            .map(d => Study.typeNames[d])
            .value()
            .join(", ");
    }

    build_details_table(div) {
        var tbl = new DescriptiveTable(),
            links = this._get_identifiers_hyperlinks_ul();
        tbl.add_tbody_tr("Data type(s)", this._get_data_types());
        tbl.add_tbody_tr("Full citation", this.data.full_citation);
        tbl.add_tbody_tr("Abstract", this.data.abstract);
        if (links.children().length > 0) tbl.add_tbody_tr("Reference hyperlink", links);
        tbl.add_tbody_tr_badge(
            "Literature review tags",
            this.data.tags.map(d => {
                return {url: getReferenceTagListUrl(this.data.assessment.id, d.id), text: d.name};
            })
        );
        if (this.data.full_text_url)
            tbl.add_tbody_tr(
                "Full text URL",
                `<a href=${this.data.full_text_url}>${this.data.full_text_url}</a>`
            );
        tbl.add_tbody_tr("COI reported", this.data.coi_reported);
        tbl.add_tbody_tr("COI details", this.data.coi_details);
        tbl.add_tbody_tr("Funding source", this.data.funding_source);
        tbl.add_tbody_tr("Study identifier", this.data.study_identifier);
        tbl.add_tbody_tr("Author contacted?", HAWCUtils.booleanCheckbox(this.data.contact_author));
        tbl.add_tbody_tr("Author contact details", this.data.ask_author, {pre: true});
        tbl.add_tbody_tr("Summary/extraction comments", this.data.summary);
        $(div).html(tbl.get_tbl());
    }

    _get_identifiers_hyperlinks_ul() {
        var ul = $("<ul>");

        this.data.identifiers.forEach(function(v) {
            if (v.url) {
                ul.append(
                    $("<li>").append(
                        $("<a>")
                            .attr("href", v.database === "HERO" ? Hero.getUrl(v.unique_id) : v.url)
                            .attr("target", "_blank")
                            .text(v.database)
                    )
                );
            }
        });

        return ul;
    }

    add_attachments_row(div, attachments) {
        if (attachments.length === 0) return;

        var tbody = div.find("table tbody"),
            ul = $("<ul>"),
            tr = $("<tr>").append("<th>Attachments</th>"),
            td = $("<td>");

        attachments.forEach(function(v) {
            ul.append(
                `<li class="pb-2">
                    <a target="_blank" href="${v.url}">${v.filename}</a>
                    <a class="btn btn-sm btn-danger float-right" title="Delete" href="${v.url_delete}">
                        <i class="fa fa-trash"></i>
                    </a>
                </li>`
            );
        });
        tbody.append(tr.append(td.append(ul)));
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = `<h4>${this.build_breadcrumbs()}</h4>`,
            $content = $('<div class="container-fluid">');

        this.render($content, modal.getModal());

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }

    render($div, $shower) {
        var self = this,
            $details = $("<div>").appendTo($div),
            displayRoB = () => {
                var render_obj = {riskofbias: self.riskofbias, display: "final"};
                render_obj = self.format_for_react(self.riskofbias);
                renderStudyDisplay(render_obj, $rob[0]);
            };
        this.build_details_table($details);
        if (this.has_riskofbias()) {
            var $rob = $('<div class="col-md-12">');
            $div.prepend($('<div class="row">').append($rob));
            if ($shower) {
                $shower.on("shown.bs.modal", displayRoB).on("shown.bs.tab", displayRoB);
            } else {
                displayRoB();
            }
        }
    }

    get_citation_row() {
        var content = [this.get_url()];
        if (!this.data.published) {
            content.push(
                '<br/><i title="Unpublished (may not be visible to the public or in some visualizations)" class="fa fa-eye-slash" aria-hidden="true"></i>'
            );
        }
        return content;
    }

    build_row() {
        return [
            this.get_citation_row(),
            this.data.full_citation,
            HAWCUtils.booleanCheckbox(this.data.bioassay),
            HAWCUtils.booleanCheckbox(this.data.epi),
            HAWCUtils.booleanCheckbox(this.data.epi_meta),
            HAWCUtils.booleanCheckbox(this.data.in_vitro),
            HAWCUtils.booleanCheckbox(this.data.eco),
        ];
    }

    format_for_react(riskofbias) {
        let scores = _.chain(riskofbias)
            .map(rob => rob.values)
            .flattenDeep()
            .value();
        return RiskOfBiasScore.format_for_react(scores);
    }
}

Study.typeNames = {
    bioassay: "Animal bioassay",
    epi: "Epidemiology",
    epi_meta: "Epidemiology meta-analysis/pooled analysis",
    in_vitro: "In vitro",
    eco: "Ecology",
};

export default Study;
