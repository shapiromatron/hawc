import _ from "lodash";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class StudyPopulation {
    constructor(data) {
        this.data = data;
        this.inclusion_criteria = _.filter(this.data.criteria, {
            criteria_type: "Inclusion",
        });
        this.exclusion_criteria = _.filter(this.data.criteria, {
            criteria_type: "Exclusion",
        });
        this.confounding_criteria = _.filter(this.data.criteria, {
            criteria_type: "Confounding",
        });
    }

    static get_detail_url(id) {
        return `/epi/study-population/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/epi/api/study-population/${id}/`, d => cb(new StudyPopulation(d)));
    }

    static displayAsModal(id) {
        StudyPopulation.get_object(id, d => d.displayAsModal());
    }

    static displayFullPager($el, id) {
        StudyPopulation.get_object(id, d => d.displayFullPager($el));
    }

    build_breadcrumbs() {
        var urls = [
            {url: this.data.study.url, name: this.data.study.short_citation},
            {url: this.data.url, name: this.data.name},
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_countries_display() {
        var countries = "";
        for (var i = 0; i < this.data.countries.length; i++) {
            countries += (countries == "" ? "" : ", ") + this.data.countries[i].name;
        }
        return countries;
    }

    build_details_table() {
        return new DescriptiveTable()
            .add_tbody_tr("Study design", this.data.design)
            .add_tbody_tr("Age profile", this.data.age_profile)
            .add_tbody_tr("Source", this.data.source)
            .add_tbody_tr("Countries", this.get_countries_display())
            .add_tbody_tr("State", this.data.state)
            .add_tbody_tr("Region", this.data.region)
            .add_tbody_tr("Eligible N", this.data.eligible_n)
            .add_tbody_tr("Invited N", this.data.invited_n)
            .add_tbody_tr("Participant N", this.data.participant_n)
            .add_tbody_tr_list("Inclusion criteria", _.map(this.inclusion_criteria, "description"))
            .add_tbody_tr_list("Exclusion criteria", _.map(this.exclusion_criteria, "description"))
            .add_tbody_tr_list(
                "Confounding criteria",
                _.map(this.confounding_criteria, "description")
            )
            .add_tbody_tr("Comments", this.data.comments)
            .get_tbl();
    }

    build_links_div() {
        var $el = $("<div>"),
            liFunc = function (d) {
                return `<li><a href="${d.url}">${d.name}</a></li>`;
            };

        $el.append("<h3>Outcomes</h3>");
        if (this.data.outcomes !== undefined && this.data.outcomes.length > 0) {
            $el.append(HAWCUtils.buildUL(this.data.outcomes, liFunc));
        } else {
            $el.append('<p class="form-text text-muted">No outcomes are available.</p>');
        }

        if (this.data.can_create_sets) {
            $el.append("<h3>Comparison sets</h3>");
            if (this.data.comparison_sets.length > 0) {
                $el.append(HAWCUtils.buildUL(this.data.comparison_sets, liFunc));
            } else {
                $el.append('<p class="form-text text-muted">No comparison sets are available.</p>');
            }
        }

        $el.append("<h3>Exposure measurements</h3>");
        if (this.data.exposures !== undefined && this.data.exposures.length > 0) {
            $el.append(HAWCUtils.buildUL(this.data.exposures, liFunc));
        } else {
            $el.append(
                '<p class="form-text text-muted">No exposure measurements are available.</p>'
            );
        }
        return $el;
    }

    displayFullPager($el) {
        $el.hide().append(this.build_details_table()).append(this.build_links_div()).fadeIn();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = `<h4>${this.build_breadcrumbs()}</h4>`,
            $content = $('<div class="container-fluid">')
                .append($('<div class="row">').append(this.build_details_table()))
                .append($('<div class="row">').append(this.build_links_div()));

        modal.addHeader(title).addBody($content).addFooter("").show({maxWidth: 1000});
    }
}

export default StudyPopulation;
