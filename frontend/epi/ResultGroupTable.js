import * as d3 from "d3";
import _ from "lodash";
import BaseTable from "shared/utils/BaseTable";
import h from "shared/utils/helpers";

class ResultGroupTable {
    constructor(res) {
        this.tbl = new BaseTable();
        this.res = res;
    }

    setVisibleCols() {
        let hasData = function(rgs, fld) {
            return _.chain(_.map(rgs, "data"))
                .map(fld)
                .map(_.isNumber)
                .some()
                .value();
        };

        this.visibleCol = {
            name: true,
            n: hasData(this.res.resultGroups, "n"),
            estimate: hasData(this.res.resultGroups, "estimate"),
            variance: hasData(this.res.resultGroups, "variance"),
            ci:
                hasData(this.res.resultGroups, "lower_ci") &&
                hasData(this.res.resultGroups, "upper_ci"),
            range:
                hasData(this.res.resultGroups, "lower_range") &&
                hasData(this.res.resultGroups, "upper_range"),
            pvalue: true,
        };
    }

    build_table() {
        let tbl = this.tbl;
        this.setVisibleCols();
        this.tbl.addHeaderRow(this.getTblHeader());
        this.tbl.setColGroup(this.getColGroups());
        _.each(this.getDataRows(), function(d) {
            tbl.addRow(d);
        });
        return tbl.getTbl();
    }

    getColGroups() {
        let weights = {
                name: 20,
                n: 10,
                estimate: 15,
                variance: 15,
                ci: 25,
                range: 15,
                pvalue: 15,
            },
            cols = _.chain(this.visibleCol)
                .map(function(v, k) {
                    if (v) return weights[k];
                })
                .filter(_.isNumber)
                .value(),
            sum = d3.sum(cols);

        return _.map(cols, d => Math.round((d / sum) * 100));
    }

    getTblHeader() {
        let d = this.res.data,
            fn = this.tbl.footnotes,
            headers = {
                name() {
                    let letter = d.trend_test
                        ? fn.add_footnote(`Trend-test result: ${d.trend_test}.`)
                        : "";
                    return `Group${letter}`;
                },
                n() {
                    return "N";
                },
                estimate() {
                    return !_.includes([null, "other"], d.estimate_type)
                        ? `Estimate (${d.estimate_type})`
                        : "Estimate";
                },
                variance() {
                    return !_.includes([null, "other"], d.variance_type)
                        ? `Variance (${d.variance_type})`
                        : "Variance";
                },
                ci() {
                    let letter = _.chain(d.results)
                        .map("ci_calc")
                        .some()
                        .value()
                        ? fn.add_footnote(
                              `Confidence intervals calculated in HAWC from distributions provided (<a href="${h.docUrlRoot}/statistical-methods/#epidemiology-v1">source</a>).`
                          )
                        : "";

                    return _.isNumber(d.ci_units)
                        ? `${d.ci_units * 100}% confidence intervals${letter}`
                        : `Confidence intervals${letter}`;
                },
                range() {
                    return "Range";
                },
                pvalue() {
                    return "<i>p</i>-value";
                },
            };

        return _.chain(this.visibleCol)
            .map(function(v, k) {
                if (v) return headers[k]();
            })
            .filter(_.String)
            .value();
    }

    getDataRows() {
        let tbl = this.tbl,
            cols = this.visibleCol;

        return _.map(this.res.resultGroups, function(rg) {
            return rg.build_tr(tbl.footnotes, cols);
        });
    }
}
export default ResultGroupTable;
