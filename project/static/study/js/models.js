var StudyVersion = function(obj, version){
    // implements requirements for js/hawc_utils Version interface
    // unpack JSON object into Study
    for (var i in obj) {
        this[i] = obj[i];
    }
    this.version = version;
    // convert datetime formats
    this.updated = new Date(this.updated);
    this.banner = this.version + ': ' + this.updated + ' by ' + this.changed_by;
};
_.extend(StudyVersion, {
    field_order: ['short_citation', 'citation', 'hero_id', 'summary', 'updated'],
});


var StudyCollection = function(objs){
    this.object_list = objs;
};
_.extend(StudyCollection, {
    get_list: function(id, cb){
        $.get('/study/api/study/?assessment_id={0}'.printf(id), function(ds){
            var objs = _.map(ds, function(d){ return new Study(d); });
            cb(new StudyCollection(objs));
        });
    },
    render: function(id, $div){
        StudyCollection.get_list(id, function(d){d.render($div);});
    },
});
StudyCollection.prototype = {
    render: function($el){
        $el.hide()
            .append(this.build_filters())
            .append(this.build_table())
            .fadeIn();

        this.registerEvents($el);
    },
    build_filters: function(){
        var $el = $('<div class="row-fluid">'),
            filters = _.chain(this.object_list)
                       .map(function(d){return d.data.study_type;})
                       .uniq()
                       .value();

        if (filters.length>1){
            $el.html(
                $('<select class="span12" size="6" multiple>').html(_.map(filters, function(d){
                    return '<option value="{0}" selected>{0}</option>'.printf(d);
                }))
            );
        }
        return $el;
    },
    build_table: function(){
        var self = this,
            tbl = new BaseTable(),
            colgroups = [25, 60, 15],
            header = ['Short citation', 'Full citation', 'Study type'];

        tbl.addHeaderRow(header);
        tbl.setColGroup(colgroups);

        _.each(this.object_list, function(d){
            tbl.addRow(d.build_row()).data('obj', d);
        });

        return tbl.getTbl();
    },
    registerEvents: function($el){
        var trs = _.map($el.find('table tbody tr'), $),
            vals;
        $el.find('select').on('change', function(e){
            vals = $(this).val();
            _.each(trs, function(tr){
                tr.toggle(vals.indexOf(tr.data('obj').data.study_type)>=0);
            });
        });
    },
};


var Study = function(data){
    this.data = data;
    this.riskofbias = [];
    if(this.data.qualities) this.unpack_riskofbias();
};
_.extend(Study, {
    get_object: function(id, cb){
        $.get('/study/api/study/{0}/'.printf(id), function(d){
            cb(new Study(d));
        });
    },
    displayAsModal: function(id){
        Study.get_object(id, function(d){d.displayAsModal();});
    },
    render: function(id, $div, $shower){
        Study.get_object(id, function(d){d.render($div, $shower);});
    },
});
Study.prototype = {
    has_riskofbias: function(){
        return this.riskofbias.length>0;
    },
    unpack_riskofbias: function(){
        // unpack risk-of-bias information and nest by domain
        var self = this,
            riskofbias = [],
            gradient_colors = d3.scale.linear()
                .domain([0, 1, 2, 3, 4])
                .range(_.values(RiskOfBias.score_shades));
        this.data.qualities.forEach(function(v, i){
            v.score_color = gradient_colors(v.score);
            v.score_text_color = String.contrasting_color(v.score_color);
            v.score_text = RiskOfBias.score_text[v.score];
            riskofbias.push(new RiskOfBias(self, v));
        });

        //construct dataset in structure for a donut plot
        this.riskofbias = d3.nest()
                                .key(function(d){return d.data.metric.domain.name;})
                                .entries(riskofbias);

        // now generate a score for each
        this.riskofbias.forEach(function(v, i){
            v.domain = v.values[0].data.metric.domain.id;
            v.domain_text = v.values[0].data.metric.domain.name;
            delete v.key;
            v.criteria = v.values;
            delete v.values;
            // we only want to calculate score for cases where answer !== N/A, or >0
            var non_zeros = d3.sum(v.criteria.map(function(v){return (v.data.score>0)?1:0;}));
            if (non_zeros>0){
                v.score = d3.round(d3.sum(v.criteria, function(v,i){return v.data.score;})/non_zeros,2);
            } else {
                v.score = 0;
            }
            v.score_text = (v.score>0) ? v.score : 'N/A';
            v.score_color = gradient_colors(v.score);
            v.score_text_color = String.contrasting_color(v.score_color);
        });

        // try to put the 'other' domain at the end
        var l = this.riskofbias.length;
        for(var i=0; i<l; i++){
            if (this.riskofbias[i].domain_text.toLowerCase() === 'other'){
                this.riskofbias.push(this.riskofbias.splice(i, 1)[0]);
                break;
            }
        }

        delete this.data.qualities;
    },
    build_breadcrumbs: function(){
        var urls = [{ url: this.data.url, name: this.data.short_citation }];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    get_name: function(){
        return this.data.short_citation;
    },
    get_url: function(){
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.short_citation);
    },
    build_details_table: function(div){
        var tbl = new DescriptiveTable(),
            links = this._get_identifiers_hyperlinks_ul();
        tbl.add_tbody_tr('Study type', this.data.study_type);
        tbl.add_tbody_tr('Full citation', this.data.full_citation);
        tbl.add_tbody_tr('Abstract', this.data.abstract);
        if (links.children().length>0) tbl.add_tbody_tr('Reference hyperlink', links);
        tbl.add_tbody_tr_list('Literature review tags', this.data.tags.map(function(d){return d.name;}));
        if (this.data.full_text_url) tbl.add_tbody_tr('Full-text link', '<a href={0}>{0}</a>'.printf(this.data.full_text_url));
        tbl.add_tbody_tr('COI reported', this.data.coi_reported);
        tbl.add_tbody_tr('COI details', this.data.coi_details);
        tbl.add_tbody_tr('Funding source', this.data.funding_source);
        tbl.add_tbody_tr('Study identifier', this.data.study_identifier);
        tbl.add_tbody_tr('Author contacted?', HAWCUtils.booleanCheckbox(this.data.contact_author));
        tbl.add_tbody_tr('Author contact details', this.data.ask_author);
        tbl.add_tbody_tr('Summary and/or extraction comments', this.data.summary);
        $(div).html(tbl.get_tbl());
    },
    _get_identifiers_hyperlinks_ul: function(){
        var ul = $('<ul>');

        this.data.identifiers.forEach(function(v){
            if (v.url){
                ul.append($('<li>').append(
                    $('<a>').attr('href', v.url).attr('target', '_blank').text(v.database)));
            }
        });

        return ul;
    },
    add_attachments_row: function(div, attachments){
        if (attachments.length===0) return;

        var tbody = div.find('table tbody'),
            ul = $('<ul>'),
            tr = $('<tr>').append('<th>Attachments</th>'),
            td = $('<td>');

        attachments.forEach(function(v){
            ul.append('<li><a target="_blank" href="{0}">{1}</a> <a class="pull-right" title="Delete {1}" href="{2}"><i class="icon-trash"></i></a></li>'.printf(v.url, v.filename, v.url_delete));
        });
        tbody.append(tr.append(td.append(ul)));
    },
    displayAsModal: function(){
        var self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">');

        this.render($content, modal.getModal());

        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 1000});
    },
    render: function($div, $shower){
        var self = this,
            $details = $('<div class="row-fluid">').appendTo($div);
        this.build_details_table($details);
        if(this.has_riskofbias()){
            var $rob = $('<div class="span12">');
            $div.prepend($('<div class="row-fluid">').append($rob));
            $shower.on('shown', function(){
                new RiskOfBias_TblCompressed(self,
                        $rob,
                        {'show_all_details_startup': false}
                );
            });
        }
    },
    build_row: function(){
        return [this.get_url(), this.data.full_citation, this.data.study_type];
    },
};
