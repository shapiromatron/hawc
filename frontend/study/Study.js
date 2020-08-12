import $ from "$";
import _ from "lodash";
import * as d3 from "d3";

import DescriptiveTable from "utils/DescriptiveTable";
import HAWCModal from "utils/HAWCModal";
import HAWCUtils from "utils/HAWCUtils";

import RiskOfBiasScore from "riskofbias/RiskOfBiasScore";
import {renderStudyDisplay} from "riskofbias/robTable/components/StudyDisplay";
import {SCORE_SHADES, SCORE_TEXT} from "riskofbias/constants";
import Donut from "riskofbias/Donut";

class Study {
    constructor(data) {
        this.data = data;
        this.riskofbias = [];
        this.final = _.find(this.data.riskofbiases, {
            final: true,
            active: true,
        });
        if (this.data.assessment.enable_risk_of_bias && this.final) {
            this.unpack_riskofbias();
        }
    }

    static get_detail_url(id) {
        return `/study/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/study/api/study/${id}/`, d => cb(new Study(d)));
    }

    static displayAsModal(id) {
        Study.get_object(id, function(d) {
            d.displayAsModal();
        });
    }

    static render(id, $div, $shower) {
        Study.get_object(id, function(d) {
            d.render($div, $shower);
        });
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
        return this.riskofbias.length > 0;
    }

    unpack_riskofbias() {
        // unpack rob information and nest by domain
        var self = this,
            riskofbias = [],
            rob_response_values = this.data.rob_response_values;

        this.final.scores.forEach(function(v, i) {
            v.score_color = SCORE_SHADES[v.score];
            v.score_text_color = String.contrasting_color(v.score_color);
            v.score_text = SCORE_TEXT[v.score];
            riskofbias.push(new RiskOfBiasScore(self, v, rob_response_values));
        });

        // group rob by domains
        this.riskofbias = d3
            .nest()
            .key(function(d) {
                return d.data.metric.domain.name;
            })
            .entries(riskofbias);

        // now generate a score for each domain (aggregating metrics)
        this.riskofbias.forEach(function(v) {
            v.domain = v.values[0].data.metric.domain.id;
            v.domain_text = v.values[0].data.metric.domain.name;
            v.domain_is_overall_confidence =
                typeof v.values[0].data.metric.domain.is_overall_confidence === "boolean"
                    ? v.values[0].data.metric.domain.is_overall_confidence
                    : false;
            v.criteria = v.values;
        });

        // try to put the 'other' domain at the end
        var l = this.riskofbias.length;
        for (var i = 0; i < l; i++) {
            if (this.riskofbias[i].domain_text.toLowerCase() === "other") {
                this.riskofbias.push(this.riskofbias.splice(i, 1)[0]);
                break;
            }
        }
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
        var data = this.data;
        return _.chain(Study.typeNames)
            .keys()
            .filter(function(d) {
                return data[d];
            })
            .map(function(d) {
                return Study.typeNames[d];
            })
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
        tbl.add_tbody_tr_list(
            "Literature review tags",
            this.data.tags.map(function(d) {
                return d.name;
            })
        );
        if (this.data.full_text_url)
            tbl.add_tbody_tr(
                "Full-text link",
                `<a href=${this.data.full_text_url}>${this.data.full_text_url}</a>`
            );
        tbl.add_tbody_tr("COI reported", this.data.coi_reported);
        tbl.add_tbody_tr("COI details", this.data.coi_details);
        tbl.add_tbody_tr("Funding source", this.data.funding_source);
        tbl.add_tbody_tr("Study identifier", this.data.study_identifier);
        tbl.add_tbody_tr("Author contacted?", HAWCUtils.booleanCheckbox(this.data.contact_author));
        tbl.add_tbody_tr("Author contact details", this.data.ask_author);
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
                            .attr("href", v.url)
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
                `<li><a target="_blank" href="${v.url}">${v.filename}</a> <a class="pull-right" title="Delete" href="${v.url_delete}"><i class="icon-trash"></i></a></li>`
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
            $details = $('<div class="row-fluid">').appendTo($div),
            displayRoB = () => {
                var render_obj = {
                    riskofbias: self.riskofbias,
                    display: "final",
                };
                render_obj = self.format_for_react(self.riskofbias);
                renderStudyDisplay(render_obj, $rob[0]);
            };
        this.build_details_table($details);
        if (this.has_riskofbias()) {
            var $rob = $('<div class="span12">');
            $div.prepend($('<div class="row-fluid">').append($rob));
            if ($shower) {
                $shower.on("shown", function() {
                    displayRoB();
                });
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
        ];
    }

    format_for_react(riskofbias) {
        let scores = _.flattenDeep(
            _.map(riskofbias, function(rob) {
                return rob.values;
            })
        );
        return RiskOfBiasScore.format_for_react(scores);
    }

    createDonutVisualization(element) {
        new Donut(this, element);
    }
}

Study.typeNames = {
    bioassay: "Animal bioassay",
    epi: "Epidemiology",
    epi_meta: "Epidemiology meta-analysis/pooled analysis",
    in_vitro: "In vitro",
};

export default Study;
