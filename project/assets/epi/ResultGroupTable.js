import _ from 'underscore';
import d3 from 'd3';

import BaseTable from 'utils/BaseTable';


class ResultGroupTable {

    constructor(res){
        this.tbl = new BaseTable();
        this.res = res;
    }

    setVisibleCols(){
        var hasData = function(rgs, fld){
            return _.chain(_.map(rgs, 'data'))
                     .pluck(fld)
                     .map(_.isNumber)
                     .any()
                     .value();
        };

        this.visibleCol = {
            'name': true,
            'n': hasData(this.res.resultGroups, 'n'),
            'estimate': hasData(this.res.resultGroups, 'estimate'),
            'variance':  hasData(this.res.resultGroups, 'variance'),
            'ci': hasData(this.res.resultGroups, 'lower_ci') && hasData(this.res.resultGroups, 'upper_ci'),
            'pvalue': true,
        };
    }

    build_table(){
        var tbl = this.tbl;
        this.setVisibleCols();
        this.tbl.addHeaderRow(this.getTblHeader());
        this.tbl.setColGroup(this.getColGroups());
        _.each(this.getDataRows(), function(d){tbl.addRow(d);});
        return tbl.getTbl();
    }

    getColGroups(){
        var weights = {
                'name': 20,
                'n': 10,
                'estimate': 15,
                'variance':  15,
                'ci': 25,
                'pvalue': 15,
            },
            cols = _.chain(this.visibleCol)
                    .map(function(v, k){ if (v) return weights[k];})
                    .filter(_.isNumber)
                    .value(),
            sum = d3.sum(cols);

        return _.map(cols, function(d){ return Math.round((d/sum)*100);});
    }

    getTblHeader(){
        var d = this.res.data,
            fn = this.tbl.footnotes,
            headers = {
                name(){
                    var txt = 'Group';
                    if (d.trend_test){
                        txt = txt + fn.add_footnote(
                            ['Trend-test result: ({0}).'.printf(d.trend_test)]);
                    }
                    return txt;
                },
                n(){
                    return 'N';
                },
                estimate(){
                    return (!_.contains([null, 'other'], d.estimate_type)) ?
                        'Estimate ({0})'.printf(d.estimate_type) :
                        'Estimate';
                },
                variance(){
                    return (!_.contains([null, 'other'], d.variance_type)) ?
                        'Variance ({0})'.printf(d.variance_type) :
                        'Variance';
                },
                ci(){
                    return (_.isNumber(d.ci_units)) ?
                        '{0}% confidence intervals'.printf(d.ci_units*100) :
                        'Confidence intervals';
                },
                pvalue(){
                    return '<i>p</i>-value';
                },
            };

        return _.chain(this.visibleCol)
                .map(function(v, k){ if (v) return headers[k]();})
                .filter(_.String)
                .value();
    }

    getDataRows(){
        var tbl = this.tbl,
            cols = this.visibleCol;
        return _.map(this.res.resultGroups, function(rg){
            return rg.build_tr(tbl.footnotes, cols);
        });
    }

}
export default ResultGroupTable;
