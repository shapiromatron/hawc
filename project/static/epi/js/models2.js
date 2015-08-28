var StudyPopulation = function(data){
    this.data = data;
    this.inclusion_criteria = _.where(this.data.criteria, {"criteria_type": "Inclusion"});
    this.exclusion_criteria = _.where(this.data.criteria, {"criteria_type": "Exclusion"});
    this.confounding_criteria = _.where(this.data.criteria, {"criteria_type": "Confounding"});
};
_.extend(StudyPopulation, {
    get_object: function(id, cb){
        $.get('/epi2/api/study-population/{0}/'.printf(id), function(d){
            cb(new StudyPopulation(d));
        });
    },
    displayAsModal: function(id){
        StudyPopulation.get_object(id, function(d){d.displayAsModal();});
    },
    displayFullPager: function($el, id){
      StudyPopulation.get_object(id, function(d){d.displayFullPager($el);});
    }
});
StudyPopulation.prototype = {
    build_breadcrumbs: function(){
        var urls = [
            { url: this.data.study.url, name: this.data.study.short_citation },
            { url: this.data.url, name: this.data.name }
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr("Study design", this.data.design)
            .add_tbody_tr("Country", this.data.country)
            .add_tbody_tr("State", this.data.state)
            .add_tbody_tr("Region", this.data.region)
            .add_tbody_tr_list("Inclusion criteria", _.pluck(this.inclusion_criteria, "description"))
            .add_tbody_tr_list("Exclusion criteria", _.pluck(this.exclusion_criteria, "description"))
            .add_tbody_tr_list("Confounding criteria", _.pluck(this.confounding_criteria, "description"))
            .get_tbl();
    },
    build_links_div: function(){
        var $el = $('<div>'),
            liFunc = function(d){
                return "<li><a href='{0}'>{1}</a></li>".printf(d.url, d.name);
            };

        $el.append("<h2>Outcomes</h2>");
        if (this.data.outcomes.length>0){
            $el.append(HAWCUtils.buildUL(this.data.outcomes, liFunc));
        } else {
            $el.append("<p class='help-block'>No outcomes are available.</p>");
        }

        if (this.data.can_create_groups){
            $el.append("<h2>Group collections</h2>");
            if (this.data.group_collections.length>0){
                $el.append(HAWCUtils.buildUL(this.data.group_collections, liFunc));
            } else {
                $el.append("<p class='help-block'>No group collections are available.</p>");
            }
        }

        $el.append("<h2>Exposures</h2>");
        if (this.data.exposures.length>0){
           $el.append(HAWCUtils.buildUL(this.data.exposures, liFunc));
        } else {
            $el.append("<p class='help-block'>No exposures are available.</p>");
        }
        return $el;
    },
    displayFullPager: function($el){
        $el.hide()
           .append(this.build_details_table())
           .append(this.build_links_div())
           .fadeIn();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">').append(this.build_details_table()),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 800});
    }
};


var Exposure = function(data){
    this.data = data;
};
_.extend(Exposure, {
    get_object: function(id, cb){
        $.get('/epi2/api/exposure/{0}/'.printf(id), function(d){
            cb(new Exposure(d));
        });
    },
    displayAsModal: function(id){
        Exposure.get_object(id, function(d){d.displayAsModal();});
    },
    displayFullPager: function($el, id){
      Exposure.get_object(id, function(d){d.displayFullPager($el);});
    }
});
Exposure.prototype = {
    build_breadcrumbs: function(){
        var urls = [
            {
                url: this.data.study_population.study.url,
                name: this.data.study_population.study.short_citation
            },
            {
                url: this.data.study_population.url,
                name: this.data.study_population.name
            },
            {
                url: this.data.url,
                name: this.data.exposure_form_definition
            }
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    get_exposure_li: function(){
        var lis = [];
        if (this.data.inhalation) lis.push("Inhalation");
        if (this.data.dermal) lis.push("Dermal");
        if (this.data.oral) lis.push("Oral");
        if (this.data.in_utero) lis.push("In utero");
        if (this.data.iv) lis.push("IV");
        if (this.data.unknown_route) lis.push("Unknown route");
        return lis;
    },
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr("Measurement metric", this.data.metric)
            .add_tbody_tr("Measurement metric units", this.data.metric_units.name)
            .add_tbody_tr("Measurement description", this.data.metric_description)
            .add_tbody_tr_list("Known exposure routes", this.get_exposure_li())
            .add_tbody_tr("Analytical method", this.data.analytical_method)
            .add_tbody_tr("Exposure description", this.data.exposure_description)
            .add_tbody_tr("Control description", this.data.control_description)
            .get_tbl();
    },
    displayFullPager: function($el){
        var tbl = this.build_details_table();
        $el.hide().append(tbl).fadeIn();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details
            .append(this.build_details_table());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }
};
