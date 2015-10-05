var MetaProtocol = function(data){
    this.data = data;
};
_.extend(MetaProtocol, {
    get_object: function(id, cb){
        $.get('/epi-meta/api/protocol/{0}/'.printf(id), function(d){
            cb(new MetaProtocol(d));
        });
    },
    displayAsModal: function(id){
        MetaProtocol.get_object(id, function(d){d.displayAsModal();});
    },
    displayFullPager: function($el, id){
      MetaProtocol.get_object(id, function(d){d.displayFullPager($el);});
    },
});
MetaProtocol.prototype = {
    build_details_table: function(div){
        return new DescriptiveTable()
            .add_tbody_tr("Description", this.data.name)
            .add_tbody_tr("Protocol type", this.data.protocol_type)
            .add_tbody_tr("Literature search strategy", this.data.lit_search_strategy)
            .add_tbody_tr("Literature search start-date", this.data.lit_search_start_date)
            .add_tbody_tr("Literature search end-date", this.data.lit_search_end_date)
            .add_tbody_tr("Literature search notes", this.data.lit_search_notes)
            .add_tbody_tr("Total references from search", this.data.total_references)
            .add_tbody_tr_list("Inclusion criteria", this.data.inclusion_criteria)
            .add_tbody_tr_list("Exclusion criteria", this.data.exclusion_criteria)
            .add_tbody_tr("Total references after inclusion/exclusion", this.data.total_studies_identified)
            .add_tbody_tr("Additional notes", this.data.notes)
            .get_tbl();
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
            $content = $('<div class="container-fluid">')
                .append(this.build_details_table())
                .append(this.build_links_div());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    },
    displayFullPager: function($el){
        $el.hide()
           .append(this.build_details_table())
           .append(this.build_links_div())
           .fadeIn();
    },
    build_links_div: function(){
        var $el = $('<div>'),
            liFunc = function(d){
                return "<li><a href='{0}'>{1}</a></li>".printf(d.url, d.label);
            };

        $el.append("<h2>Results</h2>");
        if (this.data.results.length>0){
            $el.append(HAWCUtils.buildUL(this.data.results, liFunc));
        } else {
            $el.append("<p class='help-block'>No results are available for this protocol.</p>");
        }

        return $el;
    }
};


var MetaResult = function(data){
    this.data = data;
    this.single_results = [];
    this._unpack_single_results();
};
_.extend(MetaResult, {
    get_object: function(id, cb){
        $.get('/epi-meta/api/result/{0}/'.printf(id), function(d){
            cb(new MetaResult(d));
        });
    },
    displayAsModal: function(id){
        MetaResult.get_object(id, function(d){d.displayAsModal();});
    },
    displayFullPager: function($el, id){
      MetaResult.get_object(id, function(d){d.displayFullPager($el);});
    },
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
        return new DescriptiveTable()
            .add_tbody_tr("Health outcome", this.data.health_outcome)
            .add_tbody_tr("Data location", this.data.data_location)
            .add_tbody_tr("Health outcome notes", this.data.health_outcome_notes)
            .add_tbody_tr("Exposure name", this.data.exposure_name)
            .add_tbody_tr("Exposure details", this.data.exposure_details)
            .add_tbody_tr("Number of studies", this.data.number_studies)
            .add_tbody_tr_list("Adjustment factors", this.data.adjustment_factors)
            .add_tbody_tr("N", this.data.n)
            .add_tbody_tr(this.get_statistical_metric_header(), this.data.estimateFormatted)
            .add_tbody_tr("Statistical notes", this.data.statistical_notes)
            .add_tbody_tr("Hetereogeneity notes", this.data.heterogeneity)
            .add_tbody_tr("Notes", this.data.notes)
            .get_tbl();
    },
    get_statistical_metric_header: function(){
        var txt = this.data.metric.abbreviation;
        if(this.data.ci_units){
            txt += " ({0}% CI)".printf(this.data.ci_units*100);
        }
        return txt;
    },
    has_single_results: function(){
        return(this.single_results.length>0);
    },
    build_single_results_table: function(){
        var tbl = new BaseTable();
        tbl.addHeaderRow(["Name", "Weight", "N", "Risk estimate", "Notes"]);
        tbl.setColGroup([30, 15, 15, 15, 25]);
        _.each(this.single_results, function(d){
            tbl.addRow(d.build_table_row(d));
        });
        return tbl.getTbl();
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
            $content = $('<div class="container-fluid">');

        var $singleResultsDiv = $('<div>');
        if (this.has_single_results()){
            $singleResultsDiv
                .append("<h2>Individual study results</h2>")
                .append(this.build_single_results_table());
        }
        $content
           .append(this.build_details_table())
           .append($singleResultsDiv);




        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    },
    displayFullPager: function($el){

        var $singleResultsDiv = $('<div>');
        if (this.has_single_results()){
            $singleResultsDiv
                .append("<h2>Individual study results</h2>")
                .append(this.build_single_results_table());
        }
        $el.hide()
           .append(this.build_details_table())
           .append($singleResultsDiv)
           .fadeIn();
    },
};


var SingleStudyResult = function(data){
    this.data=data
};
SingleStudyResult.prototype = {
    build_table_row: function(){
        return [
            this.study_link(),
            this.data.weight || "-",
            this.data.n || "-",
            this.data.estimateFormatted || "-",
            this.data.notes || "-",
        ];
    },
    study_link: function(){
        var txt = this.data.exposure_name;

        if(this.data.study){
            txt = '<a href="{0}">{1}</a>: '.printf(
                this.data.study.url,
                this.data.study.short_citation) + txt;
        };

        return txt;
    }
};
