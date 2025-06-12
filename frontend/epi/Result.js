import _ from "lodash";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

import ComparisonSet from "./ComparisonSet";
import ResultForestPlot from "./ResultForestPlot";
import ResultGroup from "./ResultGroup";
import ResultGroupTable from "./ResultGroupTable";

class Result {
    constructor(data) {
        this.data = data;
        this.comparison_set = new ComparisonSet(data.comparison_set);
        this.resultGroups = _.map(data.results, function (d) {
            return new ResultGroup(d);
        });
        this.factors = _.filter(this.data.factors, {
            included_in_final_model: true,
        });
        this.factors_considered = _.filter(this.data.factors, {
            included_in_final_model: false,
        });
    }

    static get_detail_url(id) {
        return `/epi/result/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/epi/api/result/${id}/`, d => cb(new Result(d)));
    }

    static displayFullPager($el, id) {
        Result.get_object(id, d => d.displayFullPager($el));
    }

    static displayAsModal(id) {
        Result.get_object(id, d => d.displayAsModal());
    }

    displayFullPager($el) {
        $el.hide()
            .append(this.build_content($el, {tabbed: false}))
            .fadeIn()
            .trigger("plotDivShown");
    }

    displayAsModal() {
        var opts = {maxWidth: 1000},
            modal = new HAWCModal(),
            title = $("<h4>").html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">');

        $content.append(this.build_content($content, {tabbed: false}));
        modal
            .addHeader(title)
            .addBody($content)
            .addFooter("")
            .show(opts, function () {
                $content.trigger("plotDivShown");
            });
    }

    build_breadcrumbs() {
        var urls = [
            {
                url: this.data.url,
                name: this.data.name,
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_tab_id() {
        return "result" + this.data.id;
    }

    build_link() {
        return `<a href="${this.data.url}">${this.data.name}</a>`;
    }

    build_tab(isActive) {
        var cls = isActive === true ? "active" : "";
        return `<a class="nav-link ${cls}" href="#${this.get_tab_id()}" data-toggle="tab">${
            this.data.name
        }</a>`;
    }

    build_content_tab(isActive) {
        var cls = isActive === true ? "active" : "",
            div = $(`<div class="tab-pane ${cls}" id="${this.get_tab_id()}">`);
        this.build_content(div, {tabbed: true});
        return div;
    }

    hasResultGroups() {
        return this.resultGroups.length > 0;
    }

    build_content($el, opts) {
        var $plotDiv = $('<div style="padding:1em">');

        $el.append(this.build_details_table(opts.tabbed));

        if (this.hasResultGroups()) {
            $el.append("<h3>Results by group</h3>").append(this.build_result_group_table());

            if (this.data.metric.showForestPlot === true) {
                $el.append("<h3>Forest plot</h3>")
                    .append($plotDiv)
                    .on("plotDivShown", this.build_forest_plot.bind(this, $plotDiv));
            }
        }

        return $el;
    }

    build_details_table(withURL) {
        var txt = withURL === true ? this.build_link() : this.data.metric.name;
        return new DescriptiveTable()
            .add_tbody_tr("Results", txt)
            .add_tbody_tr("Comparison set", this.comparison_set.build_link())
            .add_tbody_tr("Data location", this.data.data_location)
            .add_tbody_tr("Population description", this.data.population_description)
            .add_tbody_tr("Metric Description", this.data.metric_description)
            .add_tbody_tr("Metric Units", this.data.metric_units)
            .add_tbody_tr_list("Result tags", _.map(this.data.resulttags, "name"))
            .add_tbody_tr_list("Adjustment factors", _.map(this.factors, "description"))
            .add_tbody_tr_list(
                "Additional factors considered",
                _.map(this.factors_considered, "description")
            )
            .add_tbody_tr("Dose response", this.data.dose_response)
            .add_tbody_tr("Dose response details", this.data.dose_response_details)
            .add_tbody_tr("Statistical power", this.data.statistical_power)
            .add_tbody_tr("Statistical power details", this.data.statistical_power_details)
            .add_tbody_tr("Statistical test results", this.data.statistical_test_results)
            .add_tbody_tr("Prevalence incidence", this.data.prevalence_incidence)
            .add_tbody_tr("Comments", this.data.comments)
            .get_tbl();
    }

    build_result_group_table() {
        var rgd = new ResultGroupTable(this);
        return rgd.build_table();
    }

    build_forest_plot($div) {
        new ResultForestPlot(this, $div);
    }
}

export default Result;
