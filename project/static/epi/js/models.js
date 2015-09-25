var MetaProtocol = function(data){
    this.data = data;
};
_.extend(MetaProtocol, {
    get_object: function(id, cb){
        $.get('/epi/meta-protocol/{0}/json/'.printf(id), function(d){
            cb(new MetaProtocol(d));
        });
    },
    displayAsModal: function(id){
        MetaProtocol.get_object(id, function(d){d.displayAsModal();});
    }
});
MetaProtocol.prototype = {
    build_details_table: function(div){
        var tbl = new DescriptiveTable();
        tbl.add_tbody_tr("Description", this.data.name);
        tbl.add_tbody_tr("Protocol type", this.data.protocol_type);
        tbl.add_tbody_tr("Literature search strategy", this.data.lit_search_strategy);
        tbl.add_tbody_tr("Literature search start-date", this.data.lit_search_start_date);
        tbl.add_tbody_tr("Literature search end-date", this.data.lit_search_end_date);
        tbl.add_tbody_tr("Literature search notes", this.data.lit_search_notes);
        tbl.add_tbody_tr("Total references from search", this.data.total_references);
        tbl.add_tbody_tr_list("Inclusion criteria", this.data.inclusion_criteria);
        tbl.add_tbody_tr_list("Exclusion criteria", this.data.exclusion_criteria);
        tbl.add_tbody_tr("Total references after inclusion/exclusion", this.data.total_studies_identified);
        tbl.add_tbody_tr("Additional notes", this.data.notes);

        $(div).html(tbl.get_tbl());
    },
    build_breadcrumbs: function(){
        var urls = [
            { url: this.data.study.url, name: this.data.study.short_citation },
            { url: this.data.url, name: this.data.name }
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        this.build_details_table($details);

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
};


var MetaResult = function(data){
    this.data = data;
    this.single_results = [];
    this._unpack_single_results();
};
_.extend(MetaResult, {
    get_object: function(id, cb){
        $.get('/epi/meta-result/{0}/json/'.printf(id), function(d){
            cb(new MetaResult(d));
        });
    },
    displayAsModal: function(id){
        MetaResult.get_object(id, function(d){d.displayAsModal();});
    }
});
MetaResult.prototype = {
    _unpack_single_results: function(){
        var single_results = this.single_results;
        this.data.single_results.forEach(function(v,i){
            single_results.push(new SingleStudyResult(v));
        });
        this.data.single_results = [];
    },
    build_details_table: function(div){
        var tbl = new DescriptiveTable();
        tbl.add_tbody_tr("Health outcome", this.data.health_outcome);
        tbl.add_tbody_tr("Data location", this.data.data_location);
        tbl.add_tbody_tr("Health outcome notes", this.data.health_outcome_notes);
        tbl.add_tbody_tr("Exposure name", this.data.exposure_name);
        tbl.add_tbody_tr("Exposure details", this.data.exposure_details);
        tbl.add_tbody_tr("Number of studies", this.data.number_studies);
        tbl.add_tbody_tr_list("Adjustment factors", this.data.adjustment_factors);
        tbl.add_tbody_tr("N", this.data.n);
        tbl.add_tbody_tr(this.get_statistical_metric_header(), this.data.estimateFormatted);
        tbl.add_tbody_tr("Statistical notes", this.data.statistical_notes);
        tbl.add_tbody_tr("Hetereogeneity notes", this.data.heterogeneity);
        tbl.add_tbody_tr("Notes", this.data.notes);
        $(div).html(tbl.get_tbl());
    },
    get_statistical_metric_header: function(){
        var txt = this.data.statistical_metric.abbreviation;
        if(this.data.ci_units) txt += " ({0}% CI)".printf(this.data.ci_units*100);
        return txt;
    },
    has_single_results: function(){
        return(this.single_results.length>0);
    },
    build_single_results_table: function(div){
        var tbl = $('<table class="table table-condensed table-striped"></table>'),
            thead = $('<thead></thead>').append('<tr><th>Name</th><th>Weight</th><th>N</th><th>Risk Estimate</th><th>Notes</th></tr>'),
            colgroup = $('<colgroup></colgroup>').append('<col style="width: 30%;"><col style="width: 15%;"><col style="width: 15%;"><col style="width: 15%;"><col style="width: 25%;">'),
            tbody = $('<tbody></tbody>');

        this.single_results.forEach(function(v){
            v.build_table_row(tbody);
        });

        tbl.append(colgroup, thead, tbody);
        div.append(tbl);
    },
    build_breadcrumbs: function(){
        var urls = [
            { url: this.data.protocol.study.url, name: this.data.protocol.study.short_citation },
            { url: this.data.protocol.url, name: this.data.protocol.name },
            { url: this.data.url, name: this.data.label }
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    displayAsModal: function(){
        var self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $tbl = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        this.build_details_table($details);
        if(this.has_single_results()){
            $content
                .append($('<div class="row-fluid">')
                    .append('<div class="span12"><h4>Individual study-results</h4></div>'))
                .append($('<div class="row-fluid">')
                    .append($tbl));
            this.build_single_results_table($tbl);
        }

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }
};


var SingleStudyResult = function(data){
    this.data=data
};
SingleStudyResult.prototype = {
    build_table_row: function(tbody){
        var self=this,
            addIfExists = function(v){return (v) ? v : "-";},
            tr = $('<tr></tr>').appendTo(tbody),
            getValues = function(self){
                var d = {
                    "name": self.exposure_name_link(),
                    "weight": self.data.weight,
                    "notes": self.data.notes
                };
                if (self.data.outcome_group){
                    d["n"] = self.data.outcome_group.n;
                    d["risk"] = self.data.outcome_group.estimateFormatted;
                } else {
                    d["n"] = self.data.n;
                    d["risk"] = self.data.estimateFormatted;
                }
                return d;
            },
            d = getValues(this);
        tr.append('<td>{0}</td>'.printf(addIfExists(d.name)))
          .append('<td>{0}</td>'.printf(addIfExists(d.weight)))
          .append('<td>{0}</td>'.printf(addIfExists(d.n)))
          .append('<td>{0}</td>'.printf(addIfExists(d.risk)))
          .append('<td>{0}</td>'.printf(addIfExists(d.notes)))
    },
    exposure_name_link: function(){

        var txt = "";
        if(this.data.study){
            txt = '<a href="{0}" target="_blank">{1}</a>: '.printf(
                this.data.study.url,
                this.data.study.short_citation);
        };

        if(this.data.outcome_group){
            txt += '<a href="{0}" title="{1}" target="_blank">{1}</a>'.printf(
                this.data.outcome_group.assessed_outcome.url,
                this.data.outcome_group.assessed_outcome.name);
        } else {
            txt += this.data.exposure_name
        };
        return txt;
    }
};
