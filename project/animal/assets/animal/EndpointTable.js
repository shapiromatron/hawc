import $ from '$';
import _ from 'lodash';

import TableFootnotes from 'utils/TableFootnotes';


class EndpointTable {
    constructor(endpoint, tbl_id){
        this.endpoint = endpoint;
        this.tbl = $(tbl_id);
        this.footnotes = new TableFootnotes();
        this.build_table();
        this.endpoint.addObserver(this);
    }

    update(status){
        this.build_table();
    }

    build_table(){
        if (!this.endpoint.hasEGdata()){
            this.tbl.html('<p>Dose-response data unavailable.</p>');
        } else {
            this.footnotes.reset();
            this.build_header();
            this.build_body();
            this.build_footer();
            this.build_colgroup();
            this.tbl.html([this.colgroup, this.thead, this.tfoot, this.tbody]);
        }
        return this.tbl;
    }

    hasValues(val){
        return _.chain(this.endpoint.data.groups)
                .map(function(d){return d[val];})
                .some($.isNumeric)
                .value();
    }

    build_header(){
        var self = this,
            d = this.endpoint.data,
            dose = $('<th>Dose ({0})</th>'.printf(this.endpoint.dose_units)),
            tr = $('<tr>'),
            txt;

        if (this.endpoint.doses.length>1){
            $('<a title="View alternate dose" href="#"><i class="icon-chevron-right"></i></a>')
                .on('click', function(e){
                    e.preventDefault();
                    self.endpoint.toggle_dose_units();
                })
                .appendTo(dose);
        }

        tr.append(dose);

        this.hasN = this.hasValues('n');
        if(this.hasN) tr.append('<th>Number of Animals</th>');

        switch (d.data_type){
        case 'D':
        case 'DC':
            tr.append('<th>Incidence</th>')
              .append('<th>Percent Incidence</th>');
            break;
        case 'P':
            tr.append('<th>Response ({0}% CI)</th>'.printf(d.confidence_interval*100));
            break;
        case 'C':
            txt = 'Response';
            if (this.endpoint.data.response_units){
                txt += ' ({0})'.printf(this.endpoint.data.response_units);
            }
            tr.append($('<th>').text(txt));
            this.hasVariance = this.hasValues('variance');
            if(this.hasVariance) tr.append('<th>{0}</th>'.printf(d.variance_name));
            break;
        default:
            throw('Unknown data type.');
        }

        this.number_columns = tr.children().length;
        this.thead = $('<thead>').append(tr);
    }

    build_body(){
        this.tbody = $('<tbody></tbody>');
        var self = this;
        this.endpoint.data.groups.forEach(function(v, i){

            if (!v.isReported) return;

            var tr = $('<tr>'),
                dose = v.dose.toHawcString();

            dose = dose + self.endpoint.add_endpoint_group_footnotes(self.footnotes, i);

            tr.append('<td>{0}</td>'.printf(dose));

            if(self.hasN) tr.append('<td>{0}</td>'.printf(v.n || 'NR'));

            if (self.endpoint.data.data_type == 'C') {
                tr.append('<td>{0}</td>'.printf(v.response));
                if(self.hasVariance) tr.append('<td>{0}</td>'.printf(v.variance || 'NR'));
            } else if (self.endpoint.data.data_type == 'P') {
                tr.append('<td>{0}</td>'.printf(self.endpoint.get_pd_string(v)));
            } else {
                tr.append('<td>{0}</td>'.printf(v.incidence))
                  .append('<td>{0}%</td>'.printf(self.endpoint._dichotomous_percent_change_incidence(v)));
            }
            self.tbody.append(tr);
        });
    }

    build_footer(){
        var txt = this.footnotes.html_list().join('<br>');
        this.tfoot = $('<tfoot><tr><td colspan="{0}">{1}</td></tr></tfoot>'.printf(this.number_columns, txt));
    }

    build_colgroup(){
        this.colgroup = $('<colgroup></colgroup>');
        var self = this;
        for(var i=0; i<this.number_columns; i++){
            self.colgroup.append('<col style="width:{0}%;">'.printf((100/self.number_columns)));
        }
    }
}

export default EndpointTable;
