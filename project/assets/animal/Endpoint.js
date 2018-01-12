import $ from '$';
import _ from 'underscore';
import d3 from 'd3';

import BaseTable from 'utils/BaseTable';
import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';
import Observee from 'utils/Observee';

import {
    BMDLine,
} from 'bmd/models/model.js';
import Study from 'study/Study';

import AnimalGroup from './AnimalGroup';
import BMDResult from './BMDResult';
import EndpointCriticalDose from './EndpointCriticalDose';
import EndpointPlotContainer from './EndpointPlotContainer';
import EndpointTable from './EndpointTable';
import Experiment from './Experiment';


class Endpoint extends Observee {

    constructor(data, options){
        super();
        if (!data) return;  // added for edit_endpoint prototype extension
        this.options = options || {};
        this.doses = [];
        this.data = data;
        this.unpack_doses();
    }

    static get_endpoint_url(id){
        return '/ani/api/endpoint/{0}/'.printf(id);
    }

    static get_object(id, cb){
        $.get(Endpoint.get_endpoint_url(id), function(d){
            cb(new Endpoint(d));
        });
    }

    static getTagURL(assessment, slug){
        return '/ani/assessment/{0}/endpoints/tags/{1}/'.printf(assessment, slug);
    }

    static displayAsModal(id, opts){
        Endpoint.get_object(id, function(d){d.displayAsModal(opts);});
    }

    static displayInline(id, setTitle, setBody){
        Endpoint.get_object(id, (obj)=>{
            let title  = $('<h4>').html(obj.build_breadcrumbs()),
                plot_div = $('<div style="height:350px; width:350px">'),
                tbl = obj.build_endpoint_table($('<table class="table table-condensed table-striped">')),
                content = $('<div class="row-fluid">')
                    .append($('<div class="span8">').append(tbl))
                    .append($('<div class="span4">').append(plot_div));

            setTitle(title);
            setBody(content);
            obj.renderPlot(plot_div);
        });
    }

    unpack_doses(){
        if (!this.data.animal_group) return;  // added for edit_endpoint prototype extension
        this.doses = d3.nest()
               .key((d) => d.dose_units.id)
               .entries(this.data.animal_group.dosing_regime.doses);

        this.doses.forEach(function(v){ v.name = v.values[0].dose_units.name; });
        this.dose_units_id = this.options.dose_units_id || this.doses[0].key;
        this.switch_dose_units(this.dose_units_id);
    }

    toggle_dose_units(){
        var units = _.pluck(this.doses, 'key'),
            idx = units.indexOf(this.dose_units_id),
            new_idx = (idx < units.length-1) ? (idx+1) : 0;
        this._switch_dose(new_idx);
    }

    switch_dose_units(id_){
        id_ = id_.toString();
        for(var i=0; i<this.doses.length; i++){
            if(this.doses[i].key === id_){
                return this._switch_dose(i);
            }
        }
        console.log('Error: dose units not found');
    }

    _switch_dose(idx){
        // switch doses to the selected index
        try {
            var egs = this.data.groups,
                doses = this.doses[idx];

            this.dose_units_id = doses.key;
            this.dose_units = doses.name;

            egs.forEach(function(eg, i){ eg.dose = doses.values[i].dose; });

            this.notifyObservers({'status':'dose_changed'});
        } catch(err){
            console.log('error, dose index does not exist');
        }
    }

    get_name(){
        return this.data.name;
    }

    get_pod(){
        // Get point-of-departure and point-of-departure type.
        if (isFinite(this.get_bmd_special_values('BMDL'))){
            return {'type': 'BMDL', 'value': this.get_bmd_special_values('BMDL')};
        }
        if (isFinite(this.get_special_dose_text('LOEL'))){
            return {'type': 'LOEL', 'value': this.get_special_dose_text('LOEL')};
        }
        if (isFinite(this.get_special_dose_text('NOEL'))){
            return {'type': 'NOEL', 'value': this.get_special_dose_text('NOEL')};
        }
        if (isFinite(this.get_special_dose_text('FEL'))){
            return {'type': 'FEL', 'value': this.get_special_dose_text('FEL')};
        }
        return {'type': undefined, 'value': undefined};
    }

    _get_doses_by_dose_id(id){
        return _.chain(this.data.animal_group.dosing_regime.doses)
                .filter(function(d){ return d.dose_units.id === id;})
                .pluck('dose')
                .value();
    }

    _get_doses_units(){
        return _.chain(this.data.animal_group.dosing_regime.doses)
                .map(function(d){return d.dose_units;})
                .indexBy('id')
                .values()
                .value();
    }

    get_special_dose_text(name){
        // return the appropriate dose of interest
        try{
            return this.data.groups[this.data[name]].dose.toHawcString();
        }catch(err){
            return '-';
        }
    }

    get_bmd_special_values(name){
        // return the appropriate BMD output value
        try{
            return this.data.BMD.outputs[name];
        }catch(err){
            return 'none';
        }
    }

    build_endpoint_table(tbl_id){
        this.table = new EndpointTable(this, tbl_id);
        return this.table.tbl;
    }

    build_breadcrumbs(){
        var urls = [
            { url: this.data.animal_group.experiment.study.url, name: this.data.animal_group.experiment.study.short_citation },
            { url: this.data.animal_group.experiment.url, name: this.data.animal_group.experiment.name },
            { url: this.data.animal_group.url, name: this.data.animal_group.name },
            { url: this.data.url, name: this.data.name },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_pd_string(eg){
        var txt = '{0}%'.printf(eg.response);
        if(eg.lower_ci && eg.upper_ci) txt += ' ({0}-{1})'.printf(eg.lower_ci, eg.upper_ci);
        return txt;
    }

    _calculate_stdev(eg){
        // stdev is required for plotting; calculate if SE is specified
        var convert = ((this.data.data_type === 'C') &&
                       (parseInt(this.data.variance_type, 10) === 2));
        if(convert){
            if ($.isNumeric(eg.n)) {
                eg.stdev = eg.variance * Math.sqrt(eg.n);
            } else {
                eg.stdev = undefined;
            }
        } else {
            eg.stdev = eg.variance;
        }
    }

    _build_ag_dose_rows(options){

        var nGroups = this.doses[0].values.length,
            nCols = nGroups+3,
            percents = 100/(nCols+1),
            tr1 = $('<tr>'),
            tr2 = $('<tr>'),
            txt;

        // build top-row
        txt =  'Groups '.printf(this.doses[0].name);
        this.doses.forEach(function(v, i){
            txt += (i===0) ? v.name : ' ({0})'.printf(v.name);
        });

        tr1.append(`<th style="width: ${percents*2}%" rowspan="2">Endpoint</th>`)
           .append(`<th style="width: ${percents}%" rowspan="2">Organ</th>`)
           .append(`<th style="width: ${percents}%" rowspan="2">Obs. time</th>`)
           .append(`<th style="width: ${percents*nGroups}%" colspan="${nGroups}">${txt}</th>`);

        // now build header row showing available doses
        for(var i=0; i<nGroups; i++){
            var doses = this.doses.map(function(v){ return v.values[i].dose.toHawcString(); });
            txt = doses[0];
            if (doses.length>1)
                txt += ' ({0})'.printf(doses.slice(1, doses.length).join(', '));
            tr2.append('<th>{0}</th>'.printf(txt));
        }

        return {html: [tr1, tr2], ncols: nCols};
    }

    build_ag_no_dr_li(){
        return '<li><a href="{0}">{1}</a></li>'.printf(this.data.url, this.data.name);
    }

    build_ag_n_key(){
        return _.map(this.data.groups, function(v, i){return v.n || 'NR-{}'.printf(i);}).join('-');
    }

    _build_ag_n_row(options){
        return $('<tr><td>Sample Size</td><td>-</td><td>-</td>{0}</tr>'.printf(
            this.data.groups.map(function(v){return '<td>{0}</td>'.printf(v.n || '-');})));
    }

    _build_ag_response_row(footnote_object){
        var self = this, footnotes, response, td, txt, dr_control,
            data_type = this.data.data_type,
            tr = $('<tr>')
                .append(`<td><a href="${this.data.url}">${this.data.name}</a></td>`)
                .append(`<td>${this.data.organ || '-'}</td>`)
                .append(`<td>${this.data.observation_time_text || '-'}</td>`);

        this.data.groups.forEach(function(v, i){
            td = $('<td>');
            if(i === 0){
                dr_control = v;
            }
            if(!v.isReported){
                td.text('-');
            } else {
                footnotes = self.add_endpoint_group_footnotes(footnote_object, i);
                if (data_type === 'C'){
                    response = v.response.toHawcString();
                    if(v.stdev) response += ' ± {0}'.printf(v.stdev.toHawcString());
                    txt = '';
                    if(i > 0){
                        txt = self._continuous_percent_difference_from_control(v, dr_control);
                        txt = (txt === 'NR') ? '' : ' ({0}%)'.printf(txt);
                    }
                    td.html('{0}{1}{2}'.printf(response, txt, footnotes));
                } else if (data_type === 'P') {
                    td.html('{0}{1}'.printf(self.get_pd_string(v), footnotes));
                } else if (['D', 'DC'].indexOf(data_type)>=0){
                    td.html('{0}/{1} ({2}%){3}'.printf(
                        v.incidence,
                        v.n,
                        self._dichotomous_percent_change_incidence(v),
                        self.add_endpoint_group_footnotes(footnote_object, i)
                    ));
                } else {
                    console.log('unknown data-type');
                }
            }
            tr.append(td);
        });
        return tr;
    }

    _endpoint_detail_td(){
        return '<a class="endpoint-selector" href="#">{0} ({1})</a> \
                <a class="pull-right" title="View endpoint details (new window)" href="{2}"> \
                <i class="icon-share-alt"></i></a>'.printf(this.data.name, this.data.response_units, this.data.url);
    }

    build_details_table(div){
        var self = this,
            tbl = new DescriptiveTable(),
            critical_dose = function(type){
                if(self.data[type]<0) return;
                var span = $('<span>');
                new EndpointCriticalDose(self, span, type, true);
                return span;
            },
            bmd_response = function(type, showURL){
                if(self.data.bmd === null) return;
                var span = $('<span>');
                new BMDResult(self, span, type, true, showURL);
                return span;
            },
            getTaglist = function(tags, assessment_id){
                if(tags.length === 0) return false;
                var ul = $('<ul class="nav nav-pills nav-stacked">');
                tags.forEach(function(v){
                    ul.append('<li><a href="{0}">{1}</a></li>'.printf(
                      Endpoint.getTagURL(assessment_id, v.slug), v.name));
                });
                return ul;
            };

        tbl.add_tbody_tr('Endpoint name', this.data.name)
           .add_tbody_tr('System', this.data.system)
           .add_tbody_tr('Organ', this.data.organ)
           .add_tbody_tr('Effect', this.data.effect)
           .add_tbody_tr('Effect subtype', this.data.effect_subtype)
           .add_tbody_tr('Diagnostic description', this.data.diagnostic)
           .add_tbody_tr('Observation time', this.data.observation_time_text)
           .add_tbody_tr('Additional tags', getTaglist(this.data.effects, this.data.assessment))
           .add_tbody_tr('Data reported?', HAWCUtils.booleanCheckbox(this.data.data_reported))
           .add_tbody_tr('Data extracted?', HAWCUtils.booleanCheckbox(this.data.data_extracted))
           .add_tbody_tr('Values estimated?', HAWCUtils.booleanCheckbox(this.data.values_estimated))
           .add_tbody_tr('Location in literature', this.data.data_location);

        if (this.data.expected_adversity_direction>0){
            tbl.add_tbody_tr(
                'Expected response<br>adversity direction',
                this.data.expected_adversity_direction_text);
        }

        tbl.add_tbody_tr('NOEL', critical_dose('NOEL'))
           .add_tbody_tr('LOEL', critical_dose('LOEL'))
           .add_tbody_tr('FEL',  critical_dose('FEL'))
           .add_tbody_tr('BMD',  bmd_response('BMD', true))
           .add_tbody_tr('BMDL',  bmd_response('BMDL', false))
           .add_tbody_tr('Monotonicity', this.data.monotonicity)
           .add_tbody_tr('Statistical test description', this.data.statistical_test)
           .add_tbody_tr('Trend result', this.data.trend_result)
           .add_tbody_tr('Trend <i>p</i>-value', this.data.trend_value)
           .add_tbody_tr('Power notes', this.data.power_notes)
           .add_tbody_tr('Results notes', this.data.results_notes)

        $(div).html(tbl.get_tbl());
    }

    build_general_notes(div){
        var self = this,
            tbl = new BaseTable(),
            critical_dose = function(type){
                if(self.data[type]<0) return;
                var span = $('<span>');
                new EndpointCriticalDose(self, span, type, true);
                return span;
            },
            bmd_response = function(type, showURL){
                if(self.data.bmd === null) return;
                var span = $('<span>');
                new BMDResult(self, span, type, true, showURL);
                return span;
            },
            getTaglist = function(tags, assessment_id){
                if(tags.length === 0) return false;
                var ul = $('<ul class="nav nav-pills nav-stacked">');
                tags.forEach(function(v){
                    ul.append('<li><a href="{0}">{1}</a></li>'.printf(
                      Endpoint.getTagURL(assessment_id, v.slug), v.name));
                });
                return ul;
            };
        tbl.addHeaderRow(['General Notes/Methodology']);
        tbl.setColGroup([100]);
        tbl.tbody.append(this.data.endpoint_notes);
        $(div).html(tbl.getTbl());

    }

    _dichotomous_percent_change_incidence(eg){
        return (eg.isReported) ? Math.round((eg.incidence/eg.n*100), 3) : 'NR';
    }

    _continuous_percent_difference_from_control(eg, eg_control){
        var txt = 'NR';
        if (eg_control.isReported && eg.isReported && eg_control.response !== 0){
            txt = Math.round(100*((eg.response - eg_control.response)/eg_control.response), 3).toString();
        }
        return txt;
    }

    _pd_percent_difference_from_control(eg){
        return eg.response;
    }

    add_endpoint_group_footnotes(footnote_object, endpoint_group_index){
        var footnotes = [], self = this;
        if (self.data.groups[endpoint_group_index].significant){
            footnotes.push('Significantly different from control (<i>p</i> < {0})'.printf(
                self.data.groups[endpoint_group_index].significance_level));
        }
        if (self.data.LOEL == endpoint_group_index) {
            footnotes.push('LOEL (Lowest Observed Effect Level)');
        }
        if (self.data.NOEL == endpoint_group_index) {
            footnotes.push('NOEL (No Observed Effect Level)');
        }
        if (self.data.FEL == endpoint_group_index) {
            footnotes.push('FEL (Frank Effect Level)');
        }
        return footnote_object.add_footnote(footnotes);
    }

    build_endpoint_list_row(){
        var self = this,
            link = '<a href="{0}" target="_blank">{1}</a>'.printf(this.data.url, this.data.name),
            detail = $('<i class="fa fa-eye eyeEndpointModal" title="quick view" style="display: none">').click(function(){
                self.displayAsModal({complete: true});
            }),
            ep = $('<span>')
                    .append(link, detail)
                    .hover(detail.fadeIn.bind(detail), detail.fadeOut.bind(detail));

        return [
            '<a href="{0}" target="_blank">{1}</a>'.printf(
                this.data.animal_group.experiment.study.url,
                this.data.animal_group.experiment.study.short_citation),
            '<a href="{0}" target="_blank">{1}</a>'.printf(
                this.data.animal_group.experiment.url,
                this.data.animal_group.experiment.name),
            '<a href="{0}" target="_blank">{1}</a>'.printf(
                this.data.animal_group.url,
                this.data.animal_group.name),
            ep,
            this.dose_units,
            this.get_special_dose_text('NOEL'),
            this.get_special_dose_text('LOEL'),
        ];
    }

    _percent_change_control(index){
        try{
            if (this.data.data_type == 'C'){
                return this._continuous_percent_difference_from_control(
                    this.data.groups[index],
                    this.data.groups[0]);
            } else if (this.data.data_type == 'P'){
                return this._pd_percent_difference_from_control(
                    this.data.groups[index]);
            } else {
                return this._dichotomous_percent_change_incidence(
                    this.data.groups[index]);
            }
        } catch(err){
            return '-';
        }
    }

    displayAsModal(opts){
        var complete = (opts) ? opts.complete : true,
            self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $plot = $('<div style="height:300px; width:300px">'),
            $tbl = $('<table class="table table-condensed table-striped">'),
            $content = $('<div class="container-fluid">'),
            $study, $exp, $ag, $end,
            exp, ag, tabs, divs;

        if (complete){
            tabs = $('<ul class="nav nav-tabs">').append(
                '<li><a href="#modalStudy" data-toggle="tab">Study</a></li>',
                '<li><a href="#modalExp" data-toggle="tab">Experiment</a></li>',
                '<li><a href="#modalAG" data-toggle="tab">Animal Group</a></li>',
                '<li class="active"><a href="#modalEnd" data-toggle="tab">Endpoint</a></li>'
            );
            $study = $('<div class="tab-pane" id="modalStudy">');
            Study.render(this.data.animal_group.experiment.study.id,
                         $study,
                         tabs.find('a[href="#modalStudy"]'));

            $exp = $('<div class="tab-pane" id="modalExp">');
            exp = new Experiment(this.data.animal_group.experiment);
            exp.render($exp);

            $ag = $('<div class="tab-pane" id="modalAG">');
            ag = new AnimalGroup(this.data.animal_group);
            ag.render($ag);

            $end = $('<div class="tab-pane active" id="modalEnd">');
            divs = $('<div class="tab-content">').append($study, $exp, $ag, $end);
            $content.prepend(tabs, divs);
        } else {
            $end = $content;
        }

        $end
            .append($('<div class="row-fluid">')
                .append($details))
            .append($('<div class="row-fluid">')
                .append($('<div class="span7">').append($tbl))
                .append($('<div class="span5">').append($plot)));

        this.build_details_table($details);
        this.build_endpoint_table($tbl);
        modal.getModal().on('shown', function(){
            self.renderPlot($plot, true);
        });

        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 1200});
    }

    hasEGdata(){
        return (
            this.data.groups.length > 0 &&
            _.any(_.pluck(this.data.groups, 'isReported'))
        );
    }

    defaultDoseAxis(){
        var doses = _.chain(this.data.groups)
            .pluck('dose')
            .filter(function(d){return d>0;})
            .value();
        doses = d3.extent(doses);
        if (doses.length !== 2) return 'linear';
        return ((Math.log10(doses[1])-Math.log10(doses[0]))>=3) ? 'log' : 'linear';
    }

    renderPlot($div, withBMD){
        withBMD = (withBMD === undefined)? true: withBMD;
        var epc = new EndpointPlotContainer(this, $div);
        if (withBMD && this.data.bmd){
            this._render_bmd_lines(epc);
        }
        return epc;
    }

    _render_bmd_lines(epc){
        let model = this.data.bmd,
            dr = epc.plot,
            line = new BMDLine(model, dr, 'blue');

        line.render();
    }
}

export default Endpoint;
