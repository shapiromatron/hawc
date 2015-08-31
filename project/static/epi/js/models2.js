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


var Outcome = function(data){
    this.data = data;
    this.results = _.map(data.results, function(d){return new Result(d);});
    this.groups =  _.map(data.group_collections, function(d){return new GroupCollection(d);});
};
_.extend(Outcome, {
    get_object: function(id, cb){
        $.get('/epi2/api/outcome/{0}/'.printf(id), function(d){
            cb(new Outcome(d));
        });
    },
    displayAsModal: function(id){
        Outcome.get_object(id, function(d){d.displayAsModal();});
    },
    displayFullPager: function($el, id){
      Outcome.get_object(id, function(d){d.displayFullPager($el);});
    }
});
Outcome.prototype = {
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr("Name", this.data.name)
            .add_tbody_tr_list("Effect tags", _.pluck(this.data.effects, "name"))
            .add_tbody_tr("Data location", this.data.data_location)
            .add_tbody_tr("Population description", this.data.population_description)
            .add_tbody_tr("Diagnostic", this.data.diagnostic)
            .add_tbody_tr("Diagnostic description", this.data.diagnostic_description)
            .add_tbody_tr("Outcome N", this.data.outcome_n)
            .add_tbody_tr("Summary", this.data.diagnostic)
            .add_tbody_tr("Prevalence incidence", this.data.prevalence_incidence)
            .get_tbl();
    },
    build_results_tabs: function(){
        var container = $('<div>').append("<h2>Results</h2>"),
            tabs = $('<ul class="nav nav-tabs">'),
            content = $('<div class="tab-content">'),
            extra = $('<p>');

        if (this.results.length === 0){
            return container
                .append('<p class="help-block">No results are available.</p>');
        }

        _.each(this.results, function(d, i){
            var isActive = (i===0);
            tabs.append(d.build_tab(isActive));
            content.append(d.build_content_tab(isActive));
        });

        return container
            .append(tabs)
            .append(content);
    },
    get_unused_groups: function(){
        // get groups associated with no results
        var usedGroups = _.pluck(this.results, 'group');
        return _.filter(this.groups, function(d2){
            return (!_.any(_.map(usedGroups, function(d1){ return d1.isEqual(d2)})));
        });
    },
    build_groups_bullets: function(){
        var grps = this.get_unused_groups(),
            ul = HAWCUtils.buildUL(grps, function(d){
                return '<li>{0}</li>'.printf(d.build_link());
            });

        if (grps.length === 0) return;

        return $('<div>')
            .append("<h2>Group collections</h2>")
            .append(ul);
    },
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_details_table())
            .append(this.build_groups_bullets())
            .append(this.build_results_tabs())
            .fadeIn();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details
            .append(this.build_details_table())
            .append(this.build_results_tabs())
            .append(this.build_groups_bullets());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }
};


var Result = function(data){
    this.data = data;
    this.group = new GroupCollection(data.groups);
    this.factors = _.where(this.data.factors, {"included_in_final_model": true});
    this.factors_considered = _.where(this.data.factors, {"included_in_final_model": false});
};
_.extend(Result, {
    get_object: function(id, cb){
        $.get('/epi2/api/result/{0}/'.printf(id), function(d){
            cb(new Result(d));
        });
    },
    displayFullPager: function($el, id){
      Result.get_object(id, function(d){d.displayFullPager($el);});
    }
});
Result.prototype = {
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_content(null, {withSelfURL: false}))
            .fadeIn();
    },
    get_tab_id: function(){
        return "result" + this.data.id;
    },
    build_link: function(){
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.metric.metric);
    },
    build_tab: function(isActive){
        var cls = (isActive === true) ? 'class="active"' : "";
        return '<li {0}><a href="#{1}" data-toggle="tab">{2}</a></li>'.printf(
            cls,
            this.get_tab_id(),
            this.data.metric.metric
        );
    },
    build_content_tab: function(isActive){
        var cls = (isActive === true) ? 'active' : "",
            div = $('<div class="tab-pane {0}" id="{1}">'.printf(
                cls,
                this.get_tab_id()
            ));
        this.build_content(div, {withSelfURL: true});
        return div;
    },
    build_content: function($el, opts){
        $el = $el || $('<div>');

        $el
            .append(this.build_details_table(opts.withSelfURL))
            .append("<h3>Results by group</h3>")
            .append(this.build_result_group_table());

        if (this.data.metric.showForestPlot === true){
            $el
                .append("<h3>Forest plot</h3>")
                .append('<p class="help-block">TO ADD</p>');
        }

        return $el;
    },
    build_details_table: function(withURL){
        var txt = (withURL===true) ? this.build_link() : this.data.metric.metric;
        return new DescriptiveTable()
            .add_tbody_tr("Results", txt)
            .add_tbody_tr("Groups", this.group.build_link())
            .add_tbody_tr("Metric Description", this.data.metric_description)
            .add_tbody_tr_list("Factors", _.pluck(this.factors, "description"))
            .add_tbody_tr_list("Additional factors considered", _.pluck(this.factors_considered, "description"))
            .add_tbody_tr("Dose response", this.data.dose_response)
            .add_tbody_tr("Dose response details", this.data.dose_response_details)
            .add_tbody_tr("Statistical power", this.data.statistical_power)
            .add_tbody_tr("Statistical power details", this.data.statistical_power_details)
            .get_tbl();
    },
    build_result_group_table: function(){
        var self = this,
            tbl = new BaseTable(),
            headers = [
                "Group",
                "N",
                "Estimate",
                "Standard error",
                "Confidence intervals",
                "<i>p</i>-value"
            ],
            colgroups = [20, 10, 15, 15, 25, 15];

        tbl.addHeaderRow(headers);
        tbl.setColGroup(colgroups);

        _.each(this.data.results, function(d){
            tbl.addRow(self._build_result_group_tr(tbl.footnotes, d));
        });

        return tbl.getTbl();
    },
    _build_result_group_tr: function(footnotes, d){
        var tds,
            ci = "-",
            pvalue = d.p_value_qualifier,
            grp = d.group.name;

        if(d.is_main_finding){
            grp = grp + footnotes.add_footnote(["Main finding as selected by HAWC assessment authors ({0}).".printf(d.main_finding_support)]);
        }

        if (d.lower_ci && d.upper_ci){
            ci = "{0} - {1}".printf(d.lower_ci, d.upper_ci);
            // TODO: move to results-level not group level
            // TODO: change SE to variance?
            // TODO: add variance type and mean type to results?
            if (d.ci_units){
                ci = "{0} ({1}% CI)".printf(ci, d.ci_units*100);
            }
        }

        if (_.isNumber(d.p_value)){
            pvalue = "{0} {1}".printf(pvalue, d.p_value)
        }

        tds = [
            grp,
            d.n || "-",
            d.estimate || "-",
            d.se || "-",
            ci,
            pvalue
        ];

        return tds;
    }
};


var GroupCollection = function(data){
    this.data = data;
    this.groups = _.map(this.data.groups, function(d){ return new Group(d) });
};
_.extend(GroupCollection, {
    get_object: function(id, cb){
        $.get('/epi2/api/groups/{0}/'.printf(id), function(d){
            cb(new GroupCollection(d));
        });
    },
    displayFullPager: function($el, id){
      GroupCollection.get_object(id, function(d){d.displayFullPager($el);});
    }
});
GroupCollection.prototype = {
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_details_table())
            .append("<h2>Groups</h2>")
            .append(this.build_groups_table())
            .fadeIn();
    },
    build_details_table: function(){
        return new DescriptiveTable()
            .add_tbody_tr("Name", this.data.name)
            .add_tbody_tr("Description", this.data.description)
            .get_tbl();
    },
    build_groups_table: function(){
        var tbl = new BaseTable(),
            colgroups = [25, 75];

        tbl.setColGroup(colgroups);

        _.each(this.groups, function(d){
            tbl.addRow(d.build_tr());
        });

        return tbl.getTbl();
    },
    isEqual: function(other){
        return other.data.id === this.data.id;
    },
    build_link: function(){
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.name);
    },
    _build_group_tr: function(d){ // todo: make new Group object
        var ul = $('<ul>'),
            url = '<a href="{0}">{1}</a>'.printf(d.url, d.name),
            addLI = function(key, val){
                if(val){
                    ul.append("<li><strong>{0}:</strong> {1}</li>".printf(key, val));
                }
            }

        addLI("Numerical value", d.numeric);
        addLI("Comparative name", d.comparative_name);
        addLI("Sex", d.sex);
        addLI("Ethnicities", _.pluck(d.ethnicities, "name").join(", "));
        addLI("N", d.n);
        addLI("Starting N", d.starting_n);
        addLI("Fraction male", d.fraction_male);
        addLI("Fraction male calculated", d.fraction_male_calculated);  // todo: only show if above is true
        addLI("Is control?", d.isControl);

        return [url, ul];
    },
    _build_group_details: function(d){

    }
};


var Group = function(data){
    this.data = data;
    this.descriptions = _.map(this.data.descriptions, function(d){return new GroupDescription(d) });
};
_.extend(Group, {
    get_object: function(id, cb){
        $.get('/epi2/api/group/{0}/'.printf(id), function(d){
            cb(new Group(d));
        });
    },
    displayFullPager: function($el, id){
      Group.get_object(id, function(d){d.displayFullPager($el);});
    }
});
Group.prototype = {
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_details_table());

        if (this.descriptions.length>0){
            $el
                .append("<h2>Numerical group descriptions</h2>")
                .append(this.build_group_descriptions_table());
        }

        $el.fadeIn();
    },
    build_tr: function(){
        var d = this.data,
            ul = $('<ul>'),
            url = '<a href="{0}">{1}</a>'.printf(d.url, d.name),
            addLI = function(key, val){
                if(val){
                    ul.append("<li><strong>{0}:</strong> {1}</li>".printf(key, val));
                }
            }

        addLI("Numerical value", d.numeric);
        addLI("Comparative name", d.comparative_name);
        addLI("Sex", d.sex);
        addLI("Ethnicities", _.pluck(d.ethnicities, "name").join(", "));
        addLI("N", d.n);
        addLI("Starting N", d.starting_n);
        addLI("Fraction male", d.fraction_male);
        addLI("Fraction male calculated", d.fraction_male_calculated);  // todo: only show if above is true
        addLI("Is control?", d.isControl);

        return [url, ul];
    },
    build_details_table: function(){
        // todo: redundant; duplicates build_tr
        var d = this.data;
        return new DescriptiveTable()
            .add_tbody_tr("Numerical value", d.numeric)
            .add_tbody_tr("Comparative name", d.comparative_name)
            .add_tbody_tr("Sex", d.sex)
            .add_tbody_tr_list("Ethnicities", _.pluck(d.ethnicities, "name"))
            .add_tbody_tr("N", d.n)
            .add_tbody_tr("Starting N", d.starting_n)
            .add_tbody_tr("Fraction male", d.fraction_male)
            .add_tbody_tr("Fraction male calculated", d.fraction_male_calculated)  // todo: only show if above is true
            .add_tbody_tr("Is control?", d.isControl)
            .get_tbl();
    },
    build_group_descriptions_table: function(){
        var tbl = new BaseTable(),
            headers = [
                "Variable",
                "Mean",
                "Variance",
                "Lower value",
                "Upper value",
                "Calculated"
            ],
            colgroups = [25, 15, 15, 15, 15, 15]; // todo: number observations? - review data imports

        tbl.addHeaderRow(headers);
        tbl.setColGroup(colgroups);

        _.each(this.descriptions, function(d){
            tbl.addRow(d.build_tr(tbl.footnotes));
        });

        return tbl.getTbl();
    }
};



var GroupDescription = function(data){
    this.data = data;
};
GroupDescription.prototype = {
    build_tr: function(footnotes){
        var d = this.data,
            mean = "-",
            variance = "-",
            upper = "-",
            lower = "-";

        if (_.isNumber(d.mean))
            mean = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.mean, d.mean_type);
        if (_.isNumber(d.variance))
            variance = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.variance, d.variance_type);
        if (_.isNumber(d.upper))
            upper = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.upper, d.upper_type);
        if (_.isNumber(d.lower))
            lower = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.lower, d.lower_type);

        return [
            d.description,
            mean,
            variance,
            lower,
            upper,
            d.is_calculated
        ];
    }
}
