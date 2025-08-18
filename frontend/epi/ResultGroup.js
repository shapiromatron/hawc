import $ from "$";
import _ from "lodash";

import Group from "./Group";

class ResultGroup {
    constructor(data) {
        this.data = data;
        this.group = new Group(data.group);
    }

    estimateNumeric() {
        return _.isNumber(this.data.estimate);
    }

    getIntervals() {
        var ci = {
            name: this.data.group.name,
            lower_bound_interval: null,
            upper_bound_interval: null,
        };

        if (this.data.lower_ci && this.data.upper_ci) {
            ci.lower_bound_interval = this.data.lower_ci;
            ci.upper_bound_interval = this.data.upper_ci;
        } else if (
            this.data.lower_bound_interval !== null &&
            this.data.upper_bound_interval !== null
        ) {
            ci.lower_bound_interval = this.data.lower_bound_interval;
            ci.upper_bound_interval = this.data.upper_bound_interval;
        } else if (this.data.estimate !== null && this.data.se != null && this.data.n !== null) {
            ci.lower_bound_interval =
                this.data.estimate - 1.96 * this.data.se * Math.sqrt(this.data.n);
            ci.upper_bound_interval =
                this.data.estimate + 1.96 * this.data.se * Math.sqrt(this.data.n);
        }
        return ci;
    }

    _build_group_anchor(fn) {
        var txt = _.escape(this.group.data.name);

        if (this.data.is_main_finding) {
            txt += fn.add_footnote([
                `Main finding as selected by HAWC assessment authors (${this.data.main_finding_support}).`,
            ]);
        }
        return $("<a>").attr("href", this.group.url()).text(txt).popover(this.group.popover());
    }

    build_tr(fn, cols) {
        var d = this.data,
            methods = {
                name: this._build_group_anchor.bind(this, fn),
                n() {
                    return _.isFinite(d.n) ? d.n : "-";
                },
                estimate() {
                    return _.isFinite(d.estimate) ? d.estimate : "-";
                },
                variance() {
                    return _.isFinite(d.variance) ? d.variance : "-";
                },
                ci() {
                    if (_.isNumber(d.lower_ci) && _.isNumber(d.upper_ci)) {
                        return d.lower_ci < 0
                            ? `[${d.lower_ci}, ${d.upper_ci}]`
                            : `${d.lower_ci} – ${d.upper_ci}`;
                    } else {
                        return "-";
                    }
                },
                range() {
                    if (_.isNumber(d.lower_range) && _.isNumber(d.upper_range)) {
                        return d.lower_range < 0
                            ? `[${d.lower_range}, ${d.upper_range}]`
                            : `${d.lower_range} – ${d.upper_range}`;
                    } else {
                        return "-";
                    }
                },
                pvalue() {
                    return _.isNumber(d.p_value)
                        ? `${d.p_value_qualifier} ${d.p_value}`
                        : d.p_value_qualifier;
                },
            };

        return _.chain(cols)
            .map((v, k) => (v ? methods[k]() : null))
            .without(null)
            .value();
    }
}

export default ResultGroup;
