var StudyPopulation = function(data){
    this.data = data;
    this.inclusion_criteria = _.where(this.data.criteria, {"criteria_type": "Inclusion"});
    this.exclusion_criteria = _.where(this.data.criteria, {"criteria_type": "Exclusion"});
    this.confounding_criteria = _.where(this.data.criteria, {"criteria_type": "Confounding"});
};
_.extend(StudyPopulation, {
    get_object: function(id, cb){
        $.get('/epi/api/study-population/{0}/'.printf(id), function(d){
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
            .add_tbody_tr("Age profile", this.data.age_profile)
            .add_tbody_tr("Source", this.data.source)
            .add_tbody_tr("Country", this.data.country)
            .add_tbody_tr("State", this.data.state)
            .add_tbody_tr("Region", this.data.region)
            .add_tbody_tr("Eligible N", this.data.eligible_n)
            .add_tbody_tr("Invited N", this.data.invited_n)
            .add_tbody_tr("Participant N", this.data.participant_n)
            .add_tbody_tr_list("Inclusion criteria", _.pluck(this.inclusion_criteria, "description"))
            .add_tbody_tr_list("Exclusion criteria", _.pluck(this.exclusion_criteria, "description"))
            .add_tbody_tr_list("Confounding criteria", _.pluck(this.confounding_criteria, "description"))
            .add_tbody_tr("Comments", this.data.comments)
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

        if (this.data.can_create_sets){
            $el.append("<h2>Comparison sets</h2>");
            if (this.data.comparison_sets.length>0){
                $el.append(HAWCUtils.buildUL(this.data.comparison_sets, liFunc));
            } else {
                $el.append("<p class='help-block'>No comparison sets are available.</p>");
            }
        }

        $el.append("<h2>Exposure measurements</h2>");
        if (this.data.exposures.length>0){
           $el.append(HAWCUtils.buildUL(this.data.exposures, liFunc));
        } else {
            $el.append("<p class='help-block'>No exposure measurements are available.</p>");
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
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append(this.build_details_table()))
                .append($('<div class="row-fluid">').append(this.build_links_div()));

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }
};


var Exposure = function(data){
    this.data = data;
};
_.extend(Exposure, {
    get_object: function(id, cb){
        $.get('/epi/api/exposure/{0}/'.printf(id), function(d){
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
                name: this.data.name
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
    build_details_table: function(showLink){
        var link = (showLink === true) ? this.build_link() : undefined;
        return new DescriptiveTable()
            .add_tbody_tr("Name", link)
            .add_tbody_tr("What was measured", this.data.measured)
            .add_tbody_tr("Measurement metric", this.data.metric)
            .add_tbody_tr("Measurement metric units", this.data.metric_units.name)
            .add_tbody_tr("Measurement description", this.data.metric_description)
            .add_tbody_tr_list("Known exposure routes", this.get_exposure_li())
            .add_tbody_tr("Analytical method", this.data.analytical_method)
            .add_tbody_tr("Exposure description", this.data.exposure_description)
            .add_tbody_tr("Age of exposure", this.data.age_of_exposure)
            .add_tbody_tr("Duration", this.data.duration)
            .add_tbody_tr("Sampling period", this.data.sampling_period)
            .add_tbody_tr("Exposure distribution", this.data.exposure_distribution)
            .add_tbody_tr("Description", this.data.description)
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
    },
    build_link: function(){
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.name);
    },
};


var ComparisonSet = function(data){
    this.data = data;
    this.groups = _.map(this.data.groups, function(d){ return new Group(d) });
    if (this.data.exposure)
        this.exposure = new Exposure(this.data.exposure);
};
_.extend(ComparisonSet, {
    get_object: function(id, cb){
        $.get('/epi/api/comparison-set/{0}/'.printf(id), function(d){
            cb(new ComparisonSet(d));
        });
    },
    displayFullPager: function($el, id){
        ComparisonSet.get_object(id, function(d){d.displayFullPager($el);});
    },
    displayAsModal: function(id){
        ComparisonSet.get_object(id, function(d){d.displayAsModal();});
    },
});
ComparisonSet.prototype = {
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_details_div())
            .append(this.build_exposure_table())
            .append("<h2>Groups</h2>")
            .append(this.build_groups_table())
            .fadeIn();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">')
                .append(this.build_details_div())
                .append("<h2>Groups</h2>")
                .append(this.build_groups_table());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    },
    build_breadcrumbs: function(){
        var urls;
        if (this.data.outcome){
            urls = [
                {
                    url: this.data.outcome.study_population.study.url,
                    name: this.data.outcome.study_population.study.short_citation
                },
                {
                    url: this.data.outcome.study_population.url,
                    name: this.data.outcome.study_population.name
                },
                {
                    url: this.data.outcome.url,
                    name: this.data.outcome.name
                },
            ];
        } else {
            urls = [
                {
                    url: this.data.study_population.study.url,
                    name: this.data.study_population.study.short_citation
                },
                {
                    url: this.data.study_population.url,
                    name: this.data.study_population.name
                }
            ];
        }
        urls.push({
            url: this.data.url,
            name: this.data.name
        });
        return HAWCUtils.build_breadcrumbs(urls);
    },
    build_details_div: function(){
        return (this.data.description) ?
            $('<div>').html(this.data.description) :
            null;
    },
    build_exposure_table: function(){
        if (this.exposure === undefined) return;
        return $("<div>")
            .append("<h2>Exposure details</h2>")
            .append(this.exposure.build_details_table(true));
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
};


var Group = function(data){
    this.data = data;
    this.descriptions = _.map(this.data.descriptions, function(d){return new GroupDescription(d) });
};
_.extend(Group, {
    get_object: function(id, cb){
        $.get('/epi/api/group/{0}/'.printf(id), function(d){
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
    get_content: function(){
        var d = this.data,
            vals = [],
            addTuple = function(lbl, val){
                if(val) vals.push([lbl, val]);
            }
        addTuple("Numerical value", d.numeric);
        addTuple("Comparative name", d.comparative_name);
        addTuple("Sex", d.sex);
        addTuple("Ethnicities", _.pluck(d.ethnicities, "name"));
        addTuple("Eligible N", d.eligible_n)
        addTuple("Invited N", d.invited_n)
        addTuple("Participant N", d.participant_n)
        addTuple("Is control?", d.isControl);
        addTuple("Comments", d.comments);
        return vals;
    },
    build_tr: function(){
        var d = this.data,
            ul = $('<ul>'),
            url = $('<a>').attr('href', d.url).text(d.name),
            addLI = function(key, val){
                if(val){
                    ul.append("<li><strong>{0}:</strong> {1}</li>".printf(key, val));
                }
            },
            content = this.get_content();

        _.each(content, function(d){
            var val = (d[1] instanceof Array) ? d[1].join(", ") : d[1];
            addLI(d[0], val);
        });

        return [url, ul];
    },
    build_details_table: function(){
        var content = this.get_content(),
            tbl = new DescriptiveTable();

            _.each(content, function(d){
                if (d[1] instanceof Array){
                    tbl.add_tbody_tr_list(d[0], d[1]);
                } else {
                    tbl.add_tbody_tr(d[0], d[1]);
                }
            });

        return tbl.get_tbl();
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
    },
    show_tooltip: function(e){
        e.preventDefault();
        var opts = {"width": "700px", "height": "380px"},
            title = this.data.name;
            content = this.build_details_table();
        new HawcTooltip(opts).show(e, title, content);
    },
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
};


var ResultGroup = function(data){
    this.data = data;
    this.group = new Group(data.group);
};
ResultGroup.prototype = {
    show_group_tooltip: function(e){
        this.group.show_tooltip(e);
    },
    estimateNumeric: function(){
        return _.isNumber(this.data.estimate);
    },
    getCI: function(){
        var ci = {
            "name": this.data.group.name,
            "lower_ci": null,
            "upper_ci": null
        };

        if ((this.data.lower_ci !== null) && (this.data.upper_ci !== null)){
            ci.lower_ci = this.data.lower_ci;
            ci.upper_ci = this.data.upper_ci;
        } else if ((this.data.estimate !== null) && (this.data.se !== null) && (this.data.n !== null)){
            ci.lower_ci = this.data.estimate - 1.96 * this.data.se * Math.sqrt(this.data.n);
            ci.upper_ci = this.data.estimate + 1.96 * this.data.se * Math.sqrt(this.data.n);
        }
        return ci;
    },
    _build_group_anchor: function(fn){
        var txt = _.escape(this.group.data.name);

        if(this.data.is_main_finding){
            txt += fn.add_footnote([
                "Main finding as selected by HAWC assessment authors ({0})."
                    .printf(this.data.main_finding_support)
            ]);
        }
        return $("<a href='#'>")
            .on('click', this.group.show_tooltip.bind(this.group))
            .html(txt);
    },
    build_tr: function(fn, cols){
        var d = this.data,
            methods = {
                name: this._build_group_anchor.bind(this, fn),
                n: function(){
                    return (_.isFinite(d.n)) ? d.n : "-";
                },
                estimate: function(){
                    return (_.isFinite(d.estimate)) ? d.estimate : "-";
                },
                variance: function(){
                    return (_.isFinite(d.variance)) ? d.variance : "-";
                },
                ci: function(){
                    return (d.lower_ci && d.upper_ci) ?
                        "{0} - {1}".printf(d.lower_ci, d.upper_ci) :
                        "-";
                },
                pvalue: function(){
                    return (_.isNumber(d.p_value)) ?
                        "{0} {1}".printf(d.p_value_qualifier, d.p_value) :
                        d.p_value_qualifier;
                },
            }

        return _.chain(cols)
                .map(function(v, k){ return (v) ? methods[k]() : null;})
                .without(null)
                .value();
    }
};


var Outcome = function(data){
    this.data = data;
    this.results = _.map(data.results, function(d){return new Result(d);});
    this.comparison_sets = _.map(data.comparison_sets, function(d){return new ComparisonSet(d);});
};
_.extend(Outcome, {
    get_object: function(id, cb){
        $.get('/epi/api/outcome/{0}/'.printf(id), function(d){
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
            .add_tbody_tr("System", this.data.system)
            .add_tbody_tr("Effect", this.data.effect)
            .add_tbody_tr("Effect subtype", this.data.effect_subtype)
            .add_tbody_tr_list("Effect tags", _.pluck(this.data.effects, "name"))
            .add_tbody_tr("Diagnostic", this.data.diagnostic)
            .add_tbody_tr("Diagnostic description", this.data.diagnostic_description)
            .add_tbody_tr("Age of outcome measurement", this.data.age_of_measurement)
            .add_tbody_tr("Outcome N", this.data.outcome_n)
            .add_tbody_tr("Summary", this.data.summary)
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

        container.on('shown', 'a[data-toggle="tab"]', function(e){
            e.stopPropagation();
            $(this.getAttribute('href')).trigger("plotDivShown");
        });

        return container
            .append(tabs)
            .append(content);
    },
    get_unused_comparison_sets: function(){
        // get comparison sets associated with no results
        var usedSets = _.pluck(this.results, 'comparison_set');
        return _.filter(this.comparison_sets, function(d2){
            return (!_.any(_.map(usedSets, function(d1){ return d1.isEqual(d2)})));
        });
    },
    build_comparison_set_bullets: function(){
        if (this.data.can_create_sets){
            var $el = $('<div>'),
                grps = this.get_unused_comparison_sets();
            $el.append("<h2>Unused comparison sets</h2>");
            if (grps.length > 0){
                $el.append(HAWCUtils.buildUL(grps, function(d){
                    return '<li>{0}</li>'.printf(d.build_link());
                }));
            } else {
                $el.append("<p class='help-block'>No comparison sets are available.</p>");
            }
        }
        return $el;
    },
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
                name: this.data.name
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_details_table())
            .append(this.build_results_tabs())
            .append(this.build_comparison_set_bullets())
            .fadeIn(this.triggerFirstTabShown.bind(this, $el));
    },
    displayAsModal: function(){
        var opts = {maxWidth: 1000},
            modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">')
                .append(this.build_details_table())
                .append(this.build_results_tabs())
                .append(this.build_comparison_set_bullets());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show(opts, this.triggerFirstTabShown.bind(this, $content));
    },
    triggerFirstTabShown: function($el){
        $el.find('.nav-tabs .active a').trigger('shown');
    }
};


var Result = function(data){
    this.data = data;
    this.comparison_set = new ComparisonSet(data.comparison_set);
    this.resultGroups = _.map(data.results, function(d){return new ResultGroup(d);});
    this.factors = _.where(this.data.factors, {"included_in_final_model": true});
    this.factors_considered = _.where(this.data.factors, {"included_in_final_model": false});
};
_.extend(Result, {
    get_object: function(id, cb){
        $.get('/epi/api/result/{0}/'.printf(id), function(d){
            cb(new Result(d));
        });
    },
    displayFullPager: function($el, id){
      Result.get_object(id, function(d){d.displayFullPager($el);});
    },
    displayAsModal: function(id){
        Result.get_object(id, function(d){d.displayAsModal();});
    },
});
Result.prototype = {
    displayFullPager: function($el){
        $el.hide()
            .append(this.build_content($el, {tabbed: false}))
            .fadeIn()
            .trigger('plotDivShown');
    },
    displayAsModal: function(){
        var opts = {maxWidth: 1000},
            modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">');

        $content.append(this.build_content($content, {tabbed: false}));
        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show(opts, function(){
                $content.trigger('plotDivShown');
            });
    },
    build_breadcrumbs: function(){
        var urls = [
            {
                url: this.data.url,
                name: this.data.full_name
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
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
            this.data.full_name
        );
    },
    build_content_tab: function(isActive){
        var cls = (isActive === true) ? 'active' : "",
            div = $('<div class="tab-pane {0}" id="{1}">'.printf(
                cls,
                this.get_tab_id()
            ));
        this.build_content(div, {tabbed: true});
        return div;
    },
    hasResultGroups: function(){
        return this.resultGroups.length>0;
    },
    build_content: function($el, opts){
        var $plotDiv = $("<div style='padding:1em'>");

        $el
            .append(this.build_details_table(opts.tabbed));

        if (this.hasResultGroups()){
            $el
                .append("<h3>Results by group</h3>")
                .append(this.build_result_group_table());

            if (this.data.metric.showForestPlot === true){
                $el
                    .append("<h3>Forest plot</h3>")
                    .append($plotDiv)
                    .on('plotDivShown', this.build_forest_plot.bind(this, $plotDiv));
            }
        }

        return $el;
    },
    build_details_table: function(withURL){
        var txt = (withURL===true) ? this.build_link() : this.data.metric.metric;
        return new DescriptiveTable()
            .add_tbody_tr("Results", txt)
            .add_tbody_tr("Comparison set", this.comparison_set.build_link())
            .add_tbody_tr("Data location", this.data.data_location)
            .add_tbody_tr("Population description", this.data.population_description)
            .add_tbody_tr("Metric Description", this.data.metric_description)
            .add_tbody_tr_list("Adjustment factors", _.pluck(this.factors, "description"))
            .add_tbody_tr_list("Additional factors considered", _.pluck(this.factors_considered, "description"))
            .add_tbody_tr("Dose response", this.data.dose_response)
            .add_tbody_tr("Dose response details", this.data.dose_response_details)
            .add_tbody_tr("Statistical power", this.data.statistical_power)
            .add_tbody_tr("Statistical power details", this.data.statistical_power_details)
            .add_tbody_tr("Prevalence incidence", this.data.prevalence_incidence)
            .add_tbody_tr("Comments", this.data.comments)
            .get_tbl();
    },
    build_result_group_table: function(){
        var rgd = new ResultGroupTable(this);
        return rgd.build_table();
    },
    build_forest_plot: function($div){
        new ResultForestPlot(this, $div);
    },
};


var ResultForestPlot = function(res, $div, options){
    D3Plot.call(this); // call parent constructor
    this.options = options || this.default_options();
    this.set_defaults();
    this.plot_div = $div;
    this.res = res;
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(ResultForestPlot.prototype, D3Plot.prototype, {
    default_options: function(){
        return {"build_plot_startup": true};
    },
    build_plot: function(){
        this.plot_div.empty();
        this.get_dataset();
        if (!this.isPlottable()) return;
        this.get_plot_sizes();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.build_x_label();
        this.draw_visualizations();
        this.add_title();
        this.add_final_rectangle();
        this.add_menu();
        this.resize_plot_dimensions();
        this.trigger_resize();
    },
    get_dataset: function(){
        var data = this.res.data,
            estimates = _.chain(this.res.resultGroups)
                        .filter(function(d){return d.estimateNumeric();})
                        .map(function(d){
                            return {
                                "group": d,
                                "name": d.data.group.name,
                                "estimate": d.data.estimate
                            }
                        }).value(),
            lines = _.chain(estimates)
                    .map(function(d){return d.group.getCI();})
                    .filter(function(d){return _.isNumber(d.lower_ci) && _.isNumber(d.upper_ci);})
                    .value(),
            names = _.pluck(estimates, "name"),
            vals = _.chain(estimates)
                    .map(function(d){
                        return [
                            d.group.data.estimate,
                            d.group.data.lower_ci,
                            d.group.data.upper_ci
                        ];
                    })
                    .flatten()
                    .filter(function(d){ return _.isNumber(d);})
                    .value(),
            getXDomain = function(vals){
                var domain = d3.extent(vals);
                if(domain[0] === domain[1]){
                    // set reasonable defaults for domain if there is no domain.
                    if (this.scale_type === "log"){
                        domain[0] = domain[0] * 0.1;
                        domain[1] = domain[1] * 10;
                    } else {

                        if (domain[0] > 0){
                            domain[0] = 0
                        } else if(domain[0] >= -1){
                            domain[0] = -1;
                        } else {
                            domain[0] = domain[0]*2;
                        }

                        if ((domain[1] >= -1) && (domain[1] <= 1)){
                            domain[1] = 1;
                        }
                    }
                }
                return domain;
            };

        _.extend(this, {
            "title_str": data.full_name,
            "scale_type": (data.metric.isLog) ? "log" : "linear",
            "estimates": estimates,
            "lines": lines,
            "names": names,
            "x_domain": getXDomain(vals),
            "x_label_text": data.metric.metric,
        });
    },
    isPlottable: function(){
        return this.estimates.length > 0 || this.lines.length > 0;
    },
    set_defaults: function(){
        _.extend(this, {
            "padding": {
                "top": 35,
                "right": 20,
                "bottom": 40,
                "left": 20,
                "left_original": 20
            },
            "row_height": 30,
            "x_axis_settings": {
                "scale_type": "linear",
                "text_orient": "bottom",
                "axis_class": "axis x_axis",
                "number_ticks": 6,
                "x_translate": 0,
                "gridlines": true,
                "gridline_class": 'primary_gridlines x_gridlines',
                "axis_labels": true,
                "label_format": undefined
            },
            "y_axis_settings": {
                "scale_type": 'ordinal',
                "text_orient": 'left',
                "axis_class": 'axis y_axis',
                "gridlines": true,
                "gridline_class": 'primary_gridlines y_gridlines',
                "axis_labels": true,
                "label_format": undefined
            }
        });
    },
    get_plot_sizes: function(){
        this.h = this.row_height * this.names.length;
        this.w = this.plot_div.width() - this.padding.right - this.padding.left; // extra for margins
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({
            'height': (this.h + this.padding.top + this.padding.bottom + menu_spacing) + 'px'
        });
    },
    add_axes: function() {
        if (this.scale_type === "log" && this.x_domain[0] >= 1){
            this.x_domain[0] = 0.1;
        }

        _.extend(this.x_axis_settings, {
            "domain": this.x_domain,
            "rangeRound": [0, this.w],
            "y_translate": this.h,
            "scale_type": this.scale_type
        });

        _.extend(this.y_axis_settings, {
            "domain": this.names,
            "number_ticks": this.names.length,
            "rangeRound": [0, this.h],
            "x_translate": 0,
            "y_translate": 0
        });

        this.build_y_axis();
        this.build_x_axis();
    },
    draw_visualizations: function(){
        var plot = this,
            x = this.x_scale,
            y = this.y_scale,
            mid = y.rangeBand()/2;

        // vertical reference line at 1 relative risk
        this.vis.append("line")
          .attr("x1", x(1))
          .attr("y1", 0)
          .attr("x2", x(1))
          .attr("y2", this.h)
          .attr('class','reference_line');

        // estimate range
        this.estimate_range = this.vis.append("g").attr("class", "estimates_range");
        this.estimate_range.selectAll("line.temp")
          .data(this.lines)
        .enter().append("line")
          .attr("x1", function(d) { return x(d.lower_ci); })
          .attr("y1", function(d) {return  y(d.name) + mid;})
          .attr("x2", function(d) { return x(d.upper_ci); })
          .attr("y2", function(d) {return  y(d.name) + mid;})
          .attr('class','dr_err_bars');

        this.estimate_range.selectAll("line.temp")
          .data(this.lines)
        .enter().append("line")
          .attr("x1", function(d) { return x(d.lower_ci); })
          .attr("y1", function(d) {return  y(d.name) + mid*1.5;})
          .attr("x2", function(d) { return x(d.lower_ci); })
          .attr("y2", function(d) {return  y(d.name) + mid*0.5;})
          .attr('class','dr_err_bars');

        this.estimate_range.selectAll("line.temp")
          .data(this.lines)
        .enter().append("line")
          .attr("x1", function(d) { return x(d.upper_ci); })
          .attr("y1", function(d) {return  y(d.name) + mid*1.5;})
          .attr("x2", function(d) { return x(d.upper_ci); })
          .attr("y2", function(d) {return  y(d.name) + mid*0.5;})
          .attr('class','dr_err_bars');

        // central estimate
        this.estimates_group = this.vis.append("g").attr("class", "estimates");
        this.estimates = this.estimates_group.selectAll("path.dot")
          .data(this.estimates)
        .enter().append("circle")
          .attr("class", "dose_points")
          .attr("r", 7)
          .attr("cx", function(d){return x(d.estimate);})
          .attr("cy", function(d){return y(d.name) + mid;})
          .style("cursor", "pointer")
          .on('click', function(d){d.group.show_group_tooltip(d3.event);})
          .append('title').text(function(d){return "{0}: click to view exposure-group details".printf(d.estimate);});
    },
    resize_plot_dimensions: function(){
        // Resize plot based on the dimensions of the labels.
        var ylabel_width = this.plot_div.find('.y_axis')[0].getBoundingClientRect().width;
        if (this.padding.left < this.padding.left_original + ylabel_width){
            this.padding.left = this.padding.left_original + ylabel_width;
            this.build_plot();
        }
    }
});


var ResultGroupTable = function(res){
    this.tbl = new BaseTable();
    this.res = res;
};
ResultGroupTable.prototype = {
    setVisibleCols: function(){
        var hasData = function(rgs, fld){
            return _.chain(_.map(rgs, 'data'))
                     .pluck(fld)
                     .map(_.isNumber)
                     .any()
                     .value();
        }

        this.visibleCol = {
            "name": true,
            "n": hasData(this.res.resultGroups, "n"),
            "estimate": hasData(this.res.resultGroups, "estimate"),
            "variance":  hasData(this.res.resultGroups, "variance"),
            "ci": hasData(this.res.resultGroups, "lower_ci") && hasData(this.res.resultGroups, "upper_ci"),
            "pvalue": true
        }
    },
    build_table: function(){
        var tbl = this.tbl;
        this.setVisibleCols();
        this.tbl.addHeaderRow(this.getTblHeader());
        this.tbl.setColGroup(this.getColGroups());
        _.each(this.getDataRows(), function(d){tbl.addRow(d)});
        return tbl.getTbl();
    },
    getColGroups: function(){
        var weights = {
                "name": 20,
                "n": 10,
                "estimate": 15,
                "variance":  15,
                "ci": 25,
                "pvalue": 15,
            },
            cols = _.chain(this.visibleCol)
                    .map(function(v, k){ if (v) return weights[k];})
                    .filter(_.isNumber)
                    .value(),
            sum = d3.sum(cols);

        return _.map(cols, function(d){ return Math.round((d/sum)*100);});
    },
    getTblHeader: function(){
        var d = this.res.data,
            fn = this.tbl.footnotes,
            headers = {
                name: function(){
                    var txt = "Group";
                    if (d.trend_test){
                        txt = txt + fn.add_footnote(
                            ["Trend-test result: ({0}).".printf(d.trend_test)]);
                    }
                    return txt;
                },
                n: function(){
                    return "N";
                },
                estimate: function(){
                    return (!_.contains([null, "other"], d.estimate_type)) ?
                        estTxt = "Estimate ({0})".printf(d.estimate_type) :
                        "Estimate";
                },
                variance: function(){
                    return (!_.contains([null, "other"], d.variance_type)) ?
                        "Variance ({0})".printf(d.variance_type) :
                        "Variance";
                },
                ci: function(){
                    return (_.isNumber(d.ci_units)) ?
                        "{0}% confidence intervals".printf(d.ci_units*100) :
                        "Confidence intervals";
                },
                pvalue: function(){
                    return "<i>p</i>-value";
                },
            }

        return _.chain(this.visibleCol)
                .map(function(v, k){ if (v) return headers[k]();})
                .filter(_.String)
                .value();
    },
    getDataRows: function(){
        var tbl = this.tbl,
            cols = this.visibleCol;
        return _.map(this.res.resultGroups, function(rg){
            return rg.build_tr(tbl.footnotes, cols);
        });
    }
};
