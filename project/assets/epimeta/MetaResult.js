import DescriptiveTable from 'utils/DescriptiveTable';
import BaseTable from 'utils/BaseTable';
import HAWCUtils from 'utils/HAWCUtils';
import HAWCModal from 'utils/HAWCModal';

class MetaResult {

    constructor(data){
        this.data = data;
        this.single_results = [];
        this._unpack_single_results();
    }

    static get_object(id, cb){
        $.get('/epi-meta/api/result/{0}/'.printf(id), function(d){
            cb(new MetaResult(d));
        });
    }

    static displayAsModal(id){
        MetaResult.get_object(id, function(d){d.displayAsModal();});
    }

    static displayFullPager($el, id){
        MetaResult.get_object(id, function(d){d.displayFullPager($el);});
    }

    _unpack_single_results(){
        var single_results = this.single_results;
        this.data.single_results.forEach(function(v,i){
            single_results.push(new SingleStudyResult(v));
        });
        this.data.single_results = [];
    }

    build_details_table(div){
        return new DescriptiveTable()
            .add_tbody_tr('Health outcome', this.data.health_outcome)
            .add_tbody_tr('Data location', this.data.data_location)
            .add_tbody_tr('Health outcome notes', this.data.health_outcome_notes)
            .add_tbody_tr('Exposure name', this.data.exposure_name)
            .add_tbody_tr('Exposure details', this.data.exposure_details)
            .add_tbody_tr('Number of studies', this.data.number_studies)
            .add_tbody_tr_list('Adjustment factors', this.data.adjustment_factors)
            .add_tbody_tr('N', this.data.n)
            .add_tbody_tr(this.get_statistical_metric_header(), this.data.estimateFormatted)
            .add_tbody_tr('Statistical notes', this.data.statistical_notes)
            .add_tbody_tr('Hetereogeneity notes', this.data.heterogeneity)
            .add_tbody_tr('Notes', this.data.notes)
            .get_tbl();
    }

    get_statistical_metric_header(){
        var txt = this.data.metric.abbreviation;
        if(this.data.ci_units){
            txt += ' ({0}% CI)'.printf(this.data.ci_units*100);
        }
        return txt;
    }

    has_single_results(){
        return(this.single_results.length>0);
    }

    build_single_results_table(){
        var tbl = new BaseTable();
        tbl.addHeaderRow(['Name', 'Weight', 'N', 'Risk estimate', 'Notes']);
        tbl.setColGroup([30, 15, 15, 15, 25]);
        _.each(this.single_results, function(d){
            tbl.addRow(d.build_table_row(d));
        });
        return tbl.getTbl();
    }

    build_breadcrumbs(){
        var urls = [
            { url: this.data.protocol.study.url, name: this.data.protocol.study.short_citation },
            { url: this.data.protocol.url, name: this.data.protocol.name },
            { url: this.data.url, name: this.data.label },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    displayAsModal(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">');

        var $singleResultsDiv = $('<div>');
        if (this.has_single_results()){
            $singleResultsDiv
                .append('<h2>Individual study results</h2>')
                .append(this.build_single_results_table());
        }
        $content
           .append(this.build_details_table())
           .append($singleResultsDiv);




        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    }

    displayFullPager($el){

        var $singleResultsDiv = $('<div>');
        if (this.has_single_results()){
            $singleResultsDiv
                .append('<h2>Individual study results</h2>')
                .append(this.build_single_results_table());
        }
        $el.hide()
           .append(this.build_details_table())
           .append($singleResultsDiv)
           .fadeIn();
    }

}

export default MetaResult;

