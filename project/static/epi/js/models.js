var StudyPopulation = function(data){
    this.data = data;
};
_.extend(StudyPopulation, {
    get_object: function(id, cb){
        $.get('/epi/api/study-population/{0}/'.printf(id), function(d){
            cb(new StudyPopulation(d));
        });
    },
    displayAsModal: function(id){
        StudyPopulation.get_object(id, function(d){d.displayAsModal();});
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
    build_details_table: function(div){
        var tbl = new DescriptiveTable();

        tbl.add_tbody_tr("Study design", this.data.design);
        tbl.add_tbody_tr("Country", this.data.country);
        tbl.add_tbody_tr("State", this.data.state);
        tbl.add_tbody_tr("Region", this.data.region);
        tbl.add_tbody_tr_list("Inclusion criteria", this.data.inclusion_criteria);
        tbl.add_tbody_tr_list("Exclusion criteria", this.data.exclusion_criteria);
        tbl.add_tbody_tr_list("Confounding criteria", this.data.confounding_criteria);
        tbl.add_tbody_tr("N", this.data.n);
        tbl.add_tbody_tr("Sex", this.data.sex);
        tbl.add_tbody_tr_list("Ethnicities", this.data.ethnicity);
        tbl.add_tbody_tr("Fraction male", this.data.fraction_male,
                     {calculated: this.data.fraction_male_calculated});
        tbl.add_tbody_tr("Age description", this.data.age_description);
        tbl.add_tbody_tr("Age {0} (yrs)".printf(this.data.age_mean_type),
                     this.data.age_mean,
                     {calculated: this.data.age_calculated});
        tbl.add_tbody_tr("Age {0} (yrs)".printf(this.data.age_sd_type),
                     this.data.age_sd,
                     {calculated: this.data.age_calculated});
        tbl.add_tbody_tr("Age {0} (yrs)".printf(this.data.age_lower_type),
                     this.data.age_lower,
                     {calculated: this.data.age_calculated});
        tbl.add_tbody_tr("Age {0} (yrs)".printf(this.data.age_upper_type),
                     this.data.age_upper,
                     {calculated: this.data.age_calculated});

        $(div).html(tbl.get_tbl());
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
            .show({maxWidth: 800});
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
            .add_tbody_tr_list("Known exposure routes", this.get_exposure_li())
            .add_tbody_tr("Measurement metric", this.data.metric)
            .add_tbody_tr("Measurement description", this.data.metric_description)
            .add_tbody_tr("Measurement metric units", this.data.metric_units.units)
            .add_tbody_tr("Analytical method", this.data.analytical_method)
            .add_tbody_tr("Exposure description", this.data.exposure_description)
            .add_tbody_tr("Control description", this.data.control_description)
            .get_tbl();
    },
    build_egs_table: function(){
        var self = this,
            tbl = new DescriptiveTable(),
            extract_as_list = function(tbl){
                // remove descriptive table pieces and convert to list.
                var lst = [];
                tbl.find('tr').each(function(i, tr){
                    var els = $(tr).children();
                    lst.push("<strong>{0}: </strong>{1}".printf(
                        els[0].textContent,
                        els[1].textContent
                    ));
                })
                return lst;
            };

        this.data.groups.forEach(function(d){
            tbl.add_tbody_tr_list(d.description, extract_as_list(self.build_eg_table(d)));
        });
        return tbl.get_tbl()
    },
    build_eg_table: function(d){
        return new DescriptiveTable()
            .add_tbody_tr("Name", d.description)
            .add_tbody_tr("Comparison description", d.comparative_name)
            .add_tbody_tr("Exposure N", d.exposure_n)
            .add_tbody_tr("Demographic Starting N", d.starting_n)
            .add_tbody_tr("Demographic N", d.n)
            .add_tbody_tr("Sex", d.sex)
            .add_tbody_tr("Race/ethnicity", d.ethnicity.join(", "))
            .add_tbody_tr("Fraction male", d.fraction_male, {calculated: d.fraction_male_calculated})
            .add_tbody_tr("Age description", d.age_description)
            .add_tbody_tr("Age {0} (yrs)".printf(d.age_mean_type),  d.age_mean,  {calculated: d.age_calculated})
            .add_tbody_tr("Age {0} (yrs)".printf(d.age_sd_type),    d.age_sd,    {calculated: d.age_calculated})
            .add_tbody_tr("Age {0} (yrs)".printf(d.age_lower_type), d.age_lower, {calculated: d.age_calculated})
            .add_tbody_tr("Age {0} (yrs)".printf(d.age_upper_type), d.age_upper, {calculated: d.age_calculated})
            .get_tbl();
    },
    displayAsModal: function(){
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details
            .append(this.build_details_table())
            .append("<h4>Exposure groups</h4>")
            .append(this.build_egs_table());

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }
};


var AssessedOutcome = function(data){
    this.aog = [];
    this.main_finding = false;
    this.data = data;
    this._build_aogs();
};
_.extend(AssessedOutcome, {
    get_object: function(id, cb){
        $.get('/assessment/endpoint/{0}/json/'.printf(id), function(d){
            cb(new AssessedOutcome(d));
        });
    },
    displayAsModal: function(id){
        AssessedOutcome.get_object(id, function(d){d.displayAsModal();});
    }
});
AssessedOutcome.prototype = {
    _build_aogs: function(){
        this.data.groups.sort(function(a, b){
          return a.exposure_group.exposure_group_id -
                 b.exposure_group.exposure_group_id;});

        for(var i=0; i<this.data.groups.length; i++){
            var aog = new AssessedOutcomeGroup(this.data.groups[i])
            this.aog.push(aog);
            aog.data.main_finding = (aog.data.exposure_group.id === this.data.main_finding);
            if (aog.data.main_finding) this.main_finding = aog;
        }
        delete this.data.groups;
    },
    build_ao_table: function(div){
        var tbl = new DescriptiveTable();
        tbl.add_tbody_tr("Assessed outcome", this.data.name);
        tbl.add_tbody_tr("Location in literature", this.data.data_location);
        tbl.add_tbody_tr("Population description", this.data.population_description);
        tbl.add_tbody_tr("Population exposure description", this.data.exposure.exposure_description);
        tbl.add_tbody_tr("Diagnostic", this.data.diagnostic);
        tbl.add_tbody_tr("Diagnostic description", this.data.diagnostic_description);
        tbl.add_tbody_tr("Outcome N", this.data.outcome_n);
        tbl.add_tbody_tr("Summary", this.data.summary);
        if (this.main_finding) tbl.add_tbody_tr("Main finding supported?", this.data.main_finding_support);
        tbl.add_tbody_tr("Prevalence Incidence", this.data.prevalence_incidence);
        tbl.add_tbody_tr("Statistical metric presented", this.data.statistical_metric.metric);
        tbl.add_tbody_tr("Statistical metric description", this.data.statistical_metric_description);
        tbl.add_tbody_tr("Statistical power sufficient?",
            this.data.statistical_power,
            {annotate: this.data.statistical_power_details});
        tbl.add_tbody_tr("Dose response trend?",
            this.data.dose_response,
            {annotate: this.data.dose_response_details});
        tbl.add_tbody_tr("Effect tags", this.data.effects.map(function(v){return v.name;}).join(", "));
        this._ao_tbl_adjustments_columns(tbl.get_tbody());

        $(div).html(tbl.get_tbl());
    },
    _ao_tbl_adjustments_columns: function(tbody){

        var adjs = _.clone(this.data.adjustment_factors),
            confs = _.clone(this.data.confounders_considered),
            content = ['<i>None</i>'],
            tr = $('<tr>');

        for (var i = confs.length-1; i>=0; i--){
            if (adjs.indexOf(confs[i])>=0){
                confs.splice(i, 1);   // remove from array
            } else{
                confs[i] = confs[i] + "<sup>a</sup>";
            }
        };

        if (adjs.length>0 || confs.length>0){
            content = [$('<ul>')
                        .append(adjs.map(function(v){return '<li>{0}</li>'.printf(v);}))
                        .append(confs.map(function(v){return '<li>{0}</li>'.printf(v);}))];
            if(confs.length>0){
                content.push("<p><sup>a</sup> Examined but not included in final model.</p>");
            }
        }

        tr.append('<th>{0}</th>'.printf("Adjustment factors"))
          .append($('<td></td>').append(content));

        tbody.append(tr);
    },
    get_statistical_metric_header: function(){
        var txt = this.data.statistical_metric.metric;
        txt = txt.charAt(0).toUpperCase() + txt.substr(1);
        // assumes confidence interval is the same for all assessed-outcome groups
        if (this.aog.length>0) txt += this.aog[0].get_confidence_interval();
        return txt;
    },
    build_aog_table: function(div){
        var tbl = new BaseTable(),
            hasSE = this.aogs_has_se(),
            hasEstimates = this.aogs_has_estimates(),
            headers = [
                "Exposure-group",
                "N",
                "<i>p</i>-value"
            ],
            colgroups;

        if (hasEstimates) headers.splice(2, 0, this.get_statistical_metric_header());
        if (hasSE) headers.splice(headers.length-1, 0, "SE");

        switch(headers.length){
            case 5:
                colgroups = [30, 15, 25, 15, 15];
                break;
            case 4:
                colgroups = [30, 20, 30, 20];
                break;
            default:
                colgroups = [34, 33, 33];
                break;
        }
        tbl.addHeaderRow(headers);
        tbl.setColGroup(colgroups);
        this.aog.forEach(function(v){
            tbl.addRow(v.build_aog_table_row(tbl.footnotes, hasSE, hasEstimates));
        });
        $(div).html(tbl.getTbl());
    },
    has_aogs: function(){
        return (this.aog.length>0);
    },
    aogs_has_se: function(){
        var hasSE = false;
        this.aog.forEach(function(d){
            if (d.hasSE()) hasSE=true;
        });
        return hasSE;
    },
    aogs_has_estimates: function(){
        var hasEstimates = false;
        this.aog.forEach(function(d){
            if (d.hasEstimates()) hasEstimates=true;
        });
        return hasEstimates;
    },
    build_breadcrumbs: function(){
        var urls = [
            {
                url: this.data.exposure.study_population.study.url,
                name: this.data.exposure.study_population.study.short_citation
            },
            {
                url: this.data.exposure.study_population.url,
                name: this.data.exposure.study_population.name
            },
            {
                url: this.data.exposure.url,
                name: this.data.exposure.exposure_form_definition
            },
            {
                url: this.data.url,
                name: this.data.name
            }
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    build_forest_plot: function(div){
        this.plot =  new AOForestPlot(this.aog, this, div);
    },
    displayAsModal: function(){
        var self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $plot = $('<div class="span12">'),
            $tbl = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        this.build_ao_table($details);

        if(this.has_aogs()){
            $content
                .append($('<div class="row-fluid">').append($tbl))
                .append($('<div class="row-fluid">').append($plot));
            this.build_aog_table($tbl);
            modal.getModal().on('shown', function(){
                self.build_forest_plot($plot);
            });
        }

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1200});
    }
};


var AssessedOutcomeGroup = function(data){
    this.data = data;
    this.tooltip = new PlotTooltip({"width": "500px", "height": "380px"});
};
AssessedOutcomeGroup.prototype = {
    build_aog_table_row: function(footnotes, hasSE, hasEstimates){
        var self = this,
            name = this.data.exposure_group.description,
            tds,
            link;

        if(this.data.main_finding){
            name = name + footnotes.add_footnote(["Main finding as selected by HAWC assessment authors."]);
        }

        link = $('<a>')
            .attr('href', '#')
            .html(name)
            .on('click', function(e){
                e.preventDefault();
                self.tooltip.display_exposure_group_table(self, e);
            });

        tds = [
            link,
            this.data.n || "-",
            this.data.p_value_text || "-"
        ]

        if(hasEstimates){
            tds.splice(2, 0, this.data.estimateFormatted);
        }

        if(hasSE){
            tds.splice(tds.length-1, 0, this.data.se || "-");
        }

        return tds;
    },
    get_confidence_interval: function(){
        var txt = "";
        if(this.data.ci_units) txt = " ({0}% CI)".printf(this.data.ci_units*100);
        return txt;
    },
    get_ci: function(){
        var ci = {"lower_ci": undefined, "upper_ci": undefined};

        if ((this.data.lower_ci!==null) && (this.data.upper_ci!==null)){
            ci.lower_ci = this.data.lower_ci;
            ci.upper_ci = this.data.upper_ci;
        } else if ((this.data.estimate!==null) && (this.data.se!==null) && (this.data.n!==null)){
            ci.lower_ci = this.data.estimate - 1.96 * this.data.se * Math.sqrt(this.data.n);
            ci.upper_ci = this.data.estimate + 1.96 * this.data.se * Math.sqrt(this.data.n);
        }
        return ci;
    },
    hasSE: function(){
        return this.data.se !== null;
    },
    hasEstimates: function(){
        return this.data.estimate !== null || this.data.lower_ci !== null;
    },
    build_exposure_group_table: function(div){
        div.html(Exposure.prototype.build_eg_table.call(this, this.data.exposure_group));
    }
};


var AOForestPlot = function(aogs, ao, plot_div, options){
    // Assessed-outcome forest plot. Expects:
    // - an array of AssessedOutcomeGroup objects,
    // - a div to display the figure,
    // - (optionally) a title string for the plot, and
    // - (optionally) a units string for the plot, and
    // - (optionally) an options object
    D3Plot.call(this); // call parent constructor
    this.options = options || this.default_options();
    this.set_defaults();
    this.plot_div = $(plot_div);
    this.ao = ao;
    this.aogs = aogs;
    this.title_str = ao.data.name || "";
    this.x_label_text = ao.data.statistical_metric.metric || "(unitless)";
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(AOForestPlot.prototype, D3Plot.prototype, {
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
    isPlottable: function(){
        return this.estimates.length>0 || this.lines.length>0;
    },
    set_defaults: function(){
        this.padding = {top:35, right:20, bottom:40, left:20};
        this.padding.left_original = this.padding.left;
        this.x_axis_settings = {
            "scale_type": "linear",
            "text_orient": "bottom",
            "axis_class": "axis x_axis",
            "number_ticks": 6,
            "x_translate": 0,
            "gridlines": true,
            "gridline_class": 'primary_gridlines x_gridlines',
            "axis_labels": true,
            "label_format": undefined //default
        };

        this.y_axis_settings = {
            "scale_type": 'ordinal',
            "text_orient": 'left',
            "axis_class": 'axis y_axis',
            "gridlines": true,
            "gridline_class": 'primary_gridlines y_gridlines',
            "axis_labels": true,
            "label_format": undefined //default
        };

        this.row_height = 30;
    },
    get_dataset: function(){
        var estimates = [], lines = [], names = [], vals =[];

        this.aogs.forEach(function(aog, idx){
            var name = aog.data.exposure_group.description.toString();
            names.push(name);
            if(aog.data.estimate !== null){
                estimates.push({
                    "aog": aog,
                    "name": name,
                    "estimate": aog.data.estimate
                });
                vals.push(aog.data.estimate);
            }
            var ci = aog.get_ci();
            if(ci.lower_ci !== undefined){
                ci.name=name;
                lines.push(ci);
                vals.push(ci.lower_ci, ci.upper_ci);
            }
        });
        this.scale_type = (this.ao.data.statistical_metric.isLog) ? "log" : "linear";
        this.estimates = estimates;
        this.lines = lines;
        this.names = names;
        this.get_x_domain(vals);
    },
    get_x_domain: function(vals){
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

                if ((domain[1] >= -1) && (domain[1] <= 1)) domain[1] = 1;
            }
        }
        this.x_domain = domain;
    },
    get_plot_sizes: function(){
        this.h = this.row_height*this.names.length;
        this.w = this.plot_div.width() - this.padding.right - this.padding.left; // extra for margins
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
            menu_spacing) + 'px'});
    },
    add_axes: function() {
        if (this.scale_type === "log" && this.x_domain[0]>=1) this.x_domain[0]=0.1;

        $.extend(this.x_axis_settings, {
            "domain": this.x_domain,
            "rangeRound": [0, this.w],
            "y_translate": this.h,
            "scale_type": this.scale_type
        });

        $.extend(this.y_axis_settings, {
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
          .on('click', function(d){d.aog.tooltip.display_exposure_group_table(d.aog, d3.event);})
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


var AOVersion = function(obj, revision_version){
    // implements requirements for js/hawc_utils Version interface
    // unpack JSON object into Assessment
    for (var i in obj) {
        this[i] = obj[i];
    }
    // convert datetime formats
    this.created = new Date(this.created);
    this.last_updated = new Date(this.last_updated);
    this.revision_version = revision_version;
    this.banner = this.revision_version + ': ' + String(this.last_updated) + ' by ' + this.changed_by;
};
_.extend(AOVersion, {
    field_order: [
        'name', 'summary', 'statistical_metric',
        'outcome_n', 'diagnostic_description', 'prevalence_incidence',
        'created', 'last_updated']
});


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
