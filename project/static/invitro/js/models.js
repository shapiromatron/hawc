var IVEndpoint = function(data){
    this.data = data;
    this._build_ivegs();
};

IVEndpoint.prototype._build_ivegs = function(){
    this.data.experiment.egs.sort(function(a, b){
      return a.group_id - b.group_id;});
    this.egs = [];
    for(var i=0; i<this.data.experiment.egs.length; i++){
        this.egs.push(new IVEndpointGroup(this.data.experiment.egs[i]));
    }
    delete this.data.experiment.egs;

    // ajs to add: if endpoint-group data available, add to this.egs
};

IVEndpoint.prototype.build_endpoint_table = function(div){
    var tbl = $('<table class="table table-condensed table-striped"></table>'),
        colgroup = $('<colgroup></colgroup>'),
        tbody = $('<tbody></tbody>'),
        add_tbody_tr = function(description, value){
            if(value){
                tbody.append($('<tr></tr>').append($("<th>").text(description))
                                           .append($("<td>").text(value)));
            }
        }, add_tbody_tr_list = function(description, list_items){
            var ul = $('<ul></ul>').append(
                        list_items.map(function(v){return '<li>{0}</li>'.printf(v.description);})),
                tr = $('<tr></tr>')
                        .append('<th>{0}</th>'.printf(description))
                        .append($('<td></td>').append(ul));

        tbody.append(tr);
    };

    colgroup.append('<col style="width: 30%;"><col style="width: 70%;">');

    add_tbody_tr("Diagnostic", this.data.diagnostic);
    add_tbody_tr("Direction of Effect", this.data.direction_of_effect);
    add_tbody_tr("Data Type", this.data.data_type);
    add_tbody_tr("Response Trend", this.data.response_trend);
    add_tbody_tr("Response Units", this.data.response_units);

    $(div).html(tbl.append(colgroup, tbody));
};

IVEndpoint.prototype.build_eg_table = function(div){
    var self = this,
        tbl = $('<table class="table table-condensed table-striped"></table>'),
        thead = $('<thead></thead>'),
        tbody = $('<tbody></tbody>'),
        tfoot = $('<tfoot></tfoot>'),
        footnotes  = new TableFootnotes();

    // build header
    if(this.data.data_extracted){
        // ajs to add: implement more robust table since raw data available
        thead.append('<tr><th>Exposure-group</th></tr>');
    } else {
        // simple table for LOAEL/NOAEL
        thead.append('<tr><th>Dose ({0})</th></tr>'.printf(this.data.experiment.dose_units));
    }

    // build body
    this.egs.forEach(function(v, i){
        var fn_text = self.add_endpoint_group_footnotes(footnotes, i);
        tbody.append(v.build_egs_table_row(self.data.data_extracted, fn_text));
    });

    // build footer
    var tfoot_txt = footnotes.html_list().join('<br>');
    tfoot.append('<tr><td colspan="{0}">{1}</td></tr>'.printf(10, tfoot_txt));

    $(div).html(tbl.append(thead, tfoot, tbody));
};

IVEndpoint.prototype.build_breadcrumbs = function(){
    // ajs to add
    return [
        // '<a target="_blank" href="{0}">{1}</a>'
        //     .printf(this.data.study.study_url, this.data.study.short_citation),
        // '<a target="_blank" href="{0}">{1}</a>'
        //     .printf(this.data.study_population.url, this.data.study_population.name),
        // '<a target="_blank" href="{0}">{1}</a>'
        //     .printf(this.data.exposure.url, this.data.exposure.exposure_form_definition),
        // '<a target="_blank" href="{0}">{1}</a>'
        //     .printf(this.data.url, this.data.name),
    ].join('<span> / </span>');
};

IVEndpoint.prototype.add_endpoint_group_footnotes = function(footnote_object, idx){
    var footnotes = [];
    if (this.data.loael == idx) {
        footnotes.push('LOAEL (Lowest Observed Adverse Effect Level)');
    }
    if (this.data.noael == idx) {
        footnotes.push('NOAEL (No Observed Adverse Effect Level)');
    }
    return footnote_object.add_footnote(footnotes);
};


var IVEndpointGroup = function(data){
    this.data = data;
};

IVEndpointGroup.prototype.build_egs_table_row  = function(data_extracted, fn_text){
    var tr = $('<tr></tr>'), tds = [];
    if (data_extracted){
        // ajs to add robust table
    } else {
        tds.push($('<td>').html(this.data.dose + fn_text));
    }
    return tr.append(tds);
};
