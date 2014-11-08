var Endpoint = function(data){
    this.observers = [];
    this.data = data;
    this.add_confidence_intervals();
};

Endpoint.get_object = function(pk, callback){
    $.get('/ani/endpoint/{0}/json/'.printf(pk), function(d){
        callback(new Endpoint(d));
    });
};

Endpoint.getTagURL = function(assessment, slug){
    return "/ani/assessment/{0}/endpoints/tags/{1}/".printf(assessment, slug);
}

Endpoint.prototype.addObserver = function(obs){
    this.observers.push(obs);
};

Endpoint.prototype.removeObserver = function(obs){
    var observers = this.observers;
    this.observers.forEach(function(v, i){
        if (obs === v){observers.splice(i, 1);}
    });
};

Endpoint.prototype.notifyObservers = function(status){
    this.observers.forEach(function(v, i){
        v.update(status);
    });
};

Endpoint.prototype.toggle_dose_units = function(){
    // this toggles to the next dose units
    if (this.data.dose_units_index < this.data.doses.length-1){
        this._switch_dose(this.data.dose_units_index+1);
    } else {
        this._switch_dose(0);
    }
};

Endpoint.prototype._switch_dose = function(dose_index){
    // switch doses to the selected index
    try {
        var dr = this.data.dr;
        this.data.dose_units = this.data.doses[dose_index].units;
        this.data.doses[dose_index].values.forEach(function(v, i){
            dr[i].dose = v;
        });
        this.data.dose_units_index = dose_index;
        this.data.dose_units_id = this.data.doses[dose_index].units_id;
        this.notifyObservers({'status':'dose_changed'});
    } catch(err){}
};

Endpoint.prototype.get_name = function(){
    return this.data.name;
};

Endpoint.prototype.get_pod = function(){
    // Get point-of-departure and point-of-departure type.
    if (isFinite(this.get_bmd_special_values('BMDL'))){
        return {'type': 'BMDL', 'value': this.get_bmd_special_values('BMDL')};
    }
    if (isFinite(this.get_special_dose_text('LOAEL'))){
        return {'type': 'LOAEL', 'value': this.get_special_dose_text('LOAEL')};
    }
    if (isFinite(this.get_special_dose_text('NOAEL'))){
        return {'type': 'NOAEL', 'value': this.get_special_dose_text('NOAEL')};
    }
    if (isFinite(this.get_special_dose_text('FEL'))){
        return {'type': 'FEL', 'value': this.get_special_dose_text('FEL')};
    }
    return {'type': undefined, 'value': undefined};
};

Endpoint.prototype.get_special_dose_text = function(name){
    // return the appropriate dose of interest
    try{
        return this.data.dr[this.data[name]].dose;
    }catch(err){
        return 'none';
    }
};

Endpoint.prototype.get_bmd_special_values = function(name){
    // return the appropriate BMD output value
    try{
        return this.data.BMD.outputs[name];
    }catch(err){
        return 'none';
    }
};

Endpoint.prototype.build_endpoint_table = function(tbl_id){
    this.table = new EndpointTable(this, tbl_id);
    return this.table.tbl;
};

Endpoint.prototype.build_breadcrumbs = function(){
    return [
        '<a target="_blank" href="' + this.data.study.study_url + '">' + this.data.study.short_citation + '</a>',
        '<a target="_blank" href="' + this.data.experiment_url + '">' + this.data.experiment + '</a>',
        '<a target="_blank" href="' + this.data.animal_group_url + '">' + this.data.animal_group + '</a>',
        '<a target="_blank" href="' + this.data.url + '">' + this.data.name + '</a>'
    ].join('<span> >> </span>');
};

Endpoint.prototype.add_confidence_intervals = function(){
    // Add confidence interval data to dataset.
    if ((this.data !== undefined) &&
        (this.data.data_type !== undefined) &&
        (this.data.dr.length>0)) {
        if (this.data.data_type === 'C'){
            this.add_continuous_confidence_intervals();
        } else {
            this.add_dichotomous_confidence_intervals();
        }
    }
};

Endpoint.prototype.add_dichotomous_confidence_intervals = function(){
    /*
    Procedure adds confidence intervals to dichotomous datasets.
    Taken from bmds231_manual.pdf, pg 124-5

    LL = {(2np + z2 - 1) - z*sqrt[z2 - (2+1/n) + 4p(nq+1)]}/[2*(n+z2)]
    UL = {(2np + z2 + 1) + z*sqrt[z2 + (2-1/n) + 4p(nq-1)]}/[2*(n+z2)]

    - p = the observed proportion
    - n = the total number in the group in question
    - z = Z(1-alpha/2) is the inverse standard normal cumulative distribution
          function evaluated at 1-alpha/2
    - q = 1-p.

    The error bars shown in BMDS plots use alpha = 0.05 and so represent
    the 95% confidence intervals on the observed proportions (independent of
    model).
    */
    $(this.data.dr).each(function(i, v){
        var p = v.incidence/v.n,
            q = 1-p,
            z = 1.959963986120195;  // same as Math.ltqnorm(0.975);
        v.lower_limit = (((2*v.n*p + 2*z - 1) -
                         z * Math.sqrt(2*z - (2+1/v.n) + 4*p*(v.n*q+1))) / (2*(v.n+2*z)));
        v.upper_limit = (((2*v.n*p + 2*z + 1) +
                         z * Math.sqrt(2*z + (2+1/v.n) + 4*p*(v.n*q-1))) / (2*(v.n+2*z)));
    });
};

Endpoint.prototype.calculate_stdev = function(eg){
    // stdev is required for plotting; calculate if SE is specified
    var convert = ((this.data.data_type === "C") &&
                   (parseInt(this.data.variance_type, 10) === 2));
    if(convert){
        eg.stdev = eg.variance * Math.sqrt(eg.n);
    } else {
        eg.stdev = eg.variance;
    }
};

Endpoint.prototype.add_continuous_confidence_intervals = function(){
    /*
    Procedure adds confidence intervals to continuous datasets.
    Taken from bmds231_manual.pdf, pg 124

    BMDS uses a single error bar plotting routine for all continuous models.

    1. The plotting routine calculates the standard error of the mean (SEM) for
       each group. The routine divides the group-specific observed variance
       (obs standard deviation squared) by the group-specific sample size.

    2. The routine then multiplies the SEM by the Student-T percentiles (2.5th
       percentile or 97.5th percentile for the lower and upper bound,
       respectively) appropriate for the group-specific sample size
       (i.e., having degrees of freedom one less than that sample size).
       The routine adds the products to the observed means to define the lower
       and upper ends of the error bar.
    */
    var self = this;
    $(this.data.dr).each(function(i, v){
        if (v.stdev === undefined) self.calculate_stdev(v);
        var se = v.stdev/Math.sqrt(v.n),
            z = Math.Inv_tdist_05(v.n-1);
        v.lower_limit = v.response - se * z;
        v.upper_limit = v.response + se * z;
    });
};

Endpoint.prototype._build_animal_group_dose_rows = function(options){
    var self = this,
        tr1 = $('<tr></tr>').append('<th rowspan="2">Parameter</th>'),
        tr2 = $('<tr></tr>'),
        header_text,
        txt;

    this.data.doses.forEach(function(v,i){
        if(i===0){
            header_text = 'Exposure group {0}'.printf(v.units);
        } else {
            header_text += ' ({0})'.printf(v.units);
        }
    });

    tr1.append('<th colspan="{0}">{1}</th>'.printf(this.data.dr.length, header_text));

    for(var i = 0; i<this.data.dr.length; i++){
        this.data.doses.forEach(function(v, j){
            if(j===0){
                txt = v.values[i];
            } else {
                if (i!==0) txt += ' ({0})'.printf(v.values[i]);
            }
        });
        tr2.append('<th>{0}</th>'.printf(txt));
    }
    return {html: [tr1, tr2], columns_count: this.data.dr.length+1};
};

Endpoint.prototype._build_animal_group_n_row = function(options){
    return $('<tr><td>Sample Size</td>{0}</tr>'.printf(
        this.data.dr.map(function(v){return '<td>{0}</td>'.printf(v.n);})));
};

Endpoint.prototype._endpoint_detail_td = function(){
    return '<td><a class="endpoint-selector" href="#">{0} ({1})</a> \
            <a class="pull-right" title="View endpoint details (new window)" href="{2}"> \
            <i class="icon-share-alt"></i></a></td>'.printf(this.data.name, this.data.response_units, this.data.url);
};

Endpoint.prototype.build_details_table = function(div){
    var tbl = new DescriptiveTable(),
        tbody = tbl.get_tbody(),
        self = this,
        critical_dose = function(type){
            var span = $("<span>"),
                dose = new EndpointCriticalDose(self, span, type, true);
            return span;
        }, getTaglist = function(tags, assessment_id){
            if(tags.length === 0) return false;
            var ul = $('<ul class="nav nav-pills nav-stacked">');
            tags.forEach(function(v){
                ul.append('<li><a href="{0}">{1}</a></li>'.printf(Endpoint.getTagURL(assessment_id, v.slug), v.name));
            });
            return ul;
        };

    tbl.add_tbody_tr("Endpoint name", this.data.name);
    tbl.add_tbody_tr("System", this.data.system);
    tbl.add_tbody_tr("Organ", this.data.organ);
    tbl.add_tbody_tr("Effect", this.data.effect);

    if(this.data.observation_time){
        tbl.add_tbody_tr("Observation time", "{0} {1}".printf(
                            this.data.observation_time,
                            this.data.observation_time_units));
    }

    tbl.add_tbody_tr("Additional tags", getTaglist(this.data.tags, this.data.assessment_id));

    tbl.add_tbody_tr("Data reported?", HAWCUtils.booleanCheckbox(this.data.data_reported));
    tbl.add_tbody_tr("Data extracted?", HAWCUtils.booleanCheckbox(this.data.data_extracted));
    tbl.add_tbody_tr("Values estimated?", HAWCUtils.booleanCheckbox(this.data.values_estimated));
    tbl.add_tbody_tr("Location in literature", this.data.data_location);

    if(this.data.NOAEL>0) tbl.add_tbody_tr("NOAEL", critical_dose("NOAEL"));
    if(this.data.LOAEL>0) tbl.add_tbody_tr("LOAEL", critical_dose("LOAEL"));
    if(this.data.FEL>0) tbl.add_tbody_tr("FEL", critical_dose("FEL"));

    tbl.add_tbody_tr("Monotonicity", this.data.monotonicity);
    tbl.add_tbody_tr("Statistical test description", this.data.statistical_test);
    tbl.add_tbody_tr("Trend <i>p</i>-value", this.data.trend_value);
    tbl.add_tbody_tr("Results notes", this.data.results_notes);
    tbl.add_tbody_tr("General notes", this.data.endpoint_notes);

    $(div).html(tbl.get_tbl());
};

Endpoint.prototype._build_animal_group_response_row = function(footnote_object){
    var self = this, footnotes,
        tr = $('<tr>{0}</tr>'.printf(this._endpoint_detail_td()));

    if (this.data.data_type == "C"){
        var dr_control;
        this.data.dr.forEach(function(v, i){
            footnotes = self.add_endpoint_group_footnotes(footnote_object, i);
            if(i === 0){
                tr.append("<td>{0} ± {1}{2}</td>".printf(v.response, v.stdev, footnotes));
                dr_control = v;
            } else {
                tr.append("<td>{0} ± {1} ({2}%){3}</td>'".printf(v.response, v.stdev,
                    self._continuous_percent_difference_from_control(v, dr_control), footnotes));
            }
        });
    } else {
        this.data.dr.forEach(function(v, i){
        footnotes = self.add_endpoint_group_footnotes(footnote_object, i);
            tr.append("<td>{0}/{1} ({2}%){3}</td>".printf(v.incidence, v.n,
                    self._dichotomous_percent_change_incidence(v), footnotes));
        });
    }
    return tr.data('endpoint', this);
};

Endpoint.prototype._dichotomous_percent_change_incidence = function(dr){
    return Math.round((dr.incidence/dr.n*100), 3);
};

Endpoint.prototype._continuous_percent_difference_from_control = function(dr, dr_control){
    return (dr_control.response === 0) ? "-" : Math.round(100*((dr.response - dr_control.response)/dr_control.response), 3);
};

Endpoint.prototype._number_of_animals_string = function(){
    return this.data.dr.map(function(v){return v.n;}).join('-');
};

Endpoint.prototype.add_endpoint_group_footnotes = function(footnote_object, endpoint_group_index){
    var footnotes = [], self = this;
    if (self.data.dr[endpoint_group_index].significant){
        footnotes.push('Significantly different from control (<i>p</i> < {0})'.printf(self.data.dr[endpoint_group_index].significance_level));
    }
    if (self.data.LOAEL == endpoint_group_index) {
        footnotes.push('LOAEL (Lowest Observed Adverse Effect Level)');
    }
    if (self.data.NOAEL == endpoint_group_index) {
        footnotes.push('NOAEL (No Observed Adverse Effect Level)');
    }
    if (self.data.FEL == endpoint_group_index) {
        footnotes.push('FEL (Frank Effect Level)');
    }
    return footnote_object.add_footnote(footnotes);
};


var EndpointCriticalDose = function(endpoint, span, type, show_units){
    // custom field to observe dose changes and respond based on selected dose
    endpoint.addObserver(this);
    this.endpoint = endpoint;
    this.span = span;
    this.type = type;
    this.show_units = show_units;
    this.display();
};

EndpointCriticalDose.prototype.display = function(){
    var txt = "", data = this.endpoint.data;
    try {
        var txt = data.doses[data.dose_units_index].values[data[this.type]];
        if (this.show_units) txt = "{0} {1}".printf(txt, data.dose_units);
    } catch(err){}
    this.span.html(txt);
};

EndpointCriticalDose.prototype.update = function(){
    this.display();
};


var EndpointPlotContainer = function(endpoint, plot_id){
    //container used for endpoint plot organization
    this.endpoint = endpoint;
    this.plot_div = $(plot_id);
    this.plot_id = plot_id;

    if(endpoint.data.dr.length>0){
        var options = {'build_plot_startup':false};
        this.plot_style = [new Barplot(endpoint, this.plot_id, options, this),
                           new DRPlot(endpoint, this.plot_id, options, this)];
        if (endpoint.data.individual_animal_data){
            this.plot_style.splice(1, 0, new BWPlot(endpoint, this.plot_id, options, this));
        }
        this.toggle_views();
    } else {
        this.plot_div.html('<p>Plot unavailable.</p>');
    }
};

EndpointPlotContainer.prototype.add_bmd_line = function(selected_model, line_class){
    if (this.plot.add_bmd_line){this.plot.add_bmd_line(selected_model, line_class);}
};

EndpointPlotContainer.prototype.toggle_views = function(){
    // change the current plot style
    if (this.plot){this.plot.cleanup_before_change();}
    this.plot_style.unshift(this.plot_style.pop());
    this.plot = this.plot_style[0];
    this.plot.build_plot();
};

EndpointPlotContainer.prototype.add_toggle_button = function(plot){
    // add toggle to menu options to view other ways
    var ep = this;
    var options = {id:'plot_toggle',
                   cls: 'btn btn-mini',
                   title: 'View alternate visualizations',
                   text: '',
                   icon: 'icon-circle-arrow-right',
                   on_click: function(){ep.toggle_views();}};
   plot.add_menu_button(options);
};


var EndpointTable = function(endpoint, tbl_id){
    this.endpoint = endpoint;
    this.tbl = $(tbl_id);
    this.footnotes = new TableFootnotes();
    this.build_table();
    this.endpoint.addObserver(this);
};

EndpointTable.prototype.update = function(status){
    this.build_table();
};

EndpointTable.prototype.build_table = function(){
    if (this.endpoint.data.dr.length === 0){
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
};

EndpointTable.prototype.build_header = function(){
    var dose = $('<th>Dose<br>(' + this.endpoint.data.dose_units + ')</th>');
    if (this.endpoint.data.doses.length>1){
        this.dose_toggle = $('<a title="View alternate dose" href="#"><i class="icon-chevron-right"></i></a>');
        dose.append(this.dose_toggle);

        var self = this;
        this.dose_toggle.on('click', function(e){
            e.preventDefault();
            self.endpoint.toggle_dose_units();
        });
    }

    var header = $('<thead><tr></tr></thead>')
            .append(dose)
            .append('<th>Number of Animals</th>');
    if (this.endpoint.data.data_type == 'D') {
        header.append('<th>Incidence</th>')
         .append('<th>Percent Incidence</th>');
    } else {
        header.append('<th>Response</th>')
         .append('<th>{0}</th>'.printf(this.endpoint.data.variance_name));
    }
    this.number_columns = 4;
    this.thead = header;
};

EndpointTable.prototype.build_body = function(){
    this.tbody = $('<tbody></tbody>');
    var self = this;
    this.endpoint.data.dr.forEach(function(v, i){
        var tr = $('<tr></tr>'),
            dose = v.dose;

        dose = dose + self.endpoint.add_endpoint_group_footnotes(self.footnotes, i);

        tr.append('<td>{0}</td>'.printf(dose))
          .append('<td>{0}</td>'.printf(v.n));

        if (self.endpoint.data.data_type == 'C') {
            tr.append('<td>{0}</td>'.printf(v.response))
             .append('<td>{0}</td>'.printf(v.variance));
        } else {
            tr.append('<td>{0}</td>'.printf(v.incidence))
              .append('<td>{0}%</td>'.printf(self.endpoint._dichotomous_percent_change_incidence(v)));
        }
        self.tbody.append(tr);
    });
};

EndpointTable.prototype.build_footer = function(){
    var txt = this.footnotes.html_list().join('<br>');
    this.tfoot = $('<tfoot><tr><td colspan="{0}">{1}</td></tr></tfoot>'.printf(this.number_columns, txt));
};

EndpointTable.prototype.build_colgroup = function(){
    this.colgroup = $('<colgroup></colgroup>');
    var self = this;
    for(var i=0; i<this.number_columns; i++){
        self.colgroup.append('<col style="width:{0}%;">'.printf((100/self.number_columns)));
    }
};


var EndpointDetailRow = function(endpoint, div, hide_level, options){
    /*
     * Prints the endpoint as row containing consisting of an EndpointTable and
     * a DRPlot.
     */

    var plot_div_id = String.random_string(),
        table_id = String.random_string(),
        self = this;
    this.options = options || {};
    this.div = $(div);
    this.endpoint = endpoint;
    this.hide_level = hide_level || 0;

    this.div.empty();
    this.div.append('<a class="close" href="#" style="z-index:right;">×</a>');
    this.div.append('<h4>{0}</h4>'.printf(endpoint.build_breadcrumbs()));
    this.div.data('pk', endpoint.data.pk);
    this.div.append('<div class="row-fluid"><div class="span7"><table id="{0}" class="table table-condensed table-striped"></table></div><div class="span5"><div id="{1}" style="max-width:400px;" class="d3_container"></div></div></div>'.printf(table_id, plot_div_id));

    this.endpoint.build_endpoint_table($('#' + table_id));
    new EndpointPlotContainer(this.endpoint, '#' + plot_div_id);

    $(div + ' a.close').on('click', function(e){e.preventDefault(); self.toggle_view(false);});
    this.object_visible = true;
    this.div.fadeIn('fast');
};

EndpointDetailRow.prototype.toggle_view = function(show){
    var obj = (this.hide_level === 0) ? $(this.div) : this.div.parents().eq(this.hide_level);
    this.object_visible = show;
    return (show === true) ? obj.fadeIn('fast') : obj.fadeOut('fast');
};


var DRPlot = function(endpoint, div, options, parent){
    /*
     * Create a dose-response plot for a single dataset given an endpoint object
     * and the div where the object should be placed.
     */
    this.parent = parent;
    this.options = options || {build_plot_startup:true};
    this.endpoint = endpoint;
    this.plot_div = $(div);
    this.bmd = [];
    this.set_defaults(options);
    this.get_dataset_info();
    endpoint.addObserver(this);
    if (this.options.build_plot_startup){this.build_plot();}
};

DRPlot.prototype = new D3Plot();
DRPlot.prototype.constructor = DRPlot;

DRPlot.prototype.update = function(status){
    if (status.status === "dose_changed") this.dose_scale_change();
};

DRPlot.prototype.dose_scale_change = function(){
    // get latest data from endpoint
    this.clear_bmd_lines('d3_bmd_selected');
    this.get_dataset_info();

    //update if plot is live
    if (this.parent && this.parent.plot === this){
        if (this.x_axis_settings.scale_type == 'linear'){
            this.x_axis_settings.domain = [this.min_x-this.max_x*this.buff, this.max_x*(1+this.buff)];
        } else {
            this.x_axis_settings.domain = [this.min_x/10, this.max_x*(1+this.buff)];
        }
        this.x_scale = this._build_scale(this.x_axis_settings);

        this.build_x_label();
        this.add_selected_endpoint_BMD();
        this.x_axis_change_chart_update();
    }
};

DRPlot.prototype.build_plot = function() {
    try{
        delete this.error_bars_vertical;
        delete this.error_bars_upper;
        delete this.error_bars_lower;
        delete this.error_bar_group;
        this.clear_bmd_lines();
    }catch (err){}
    this.plot_div.html('');
    this.get_plot_sizes();
    this.build_plot_skeleton(true);
    this.add_axes();
    this.add_dr_error_bars();
    this.add_dose_response();
    this.add_selected_endpoint_BMD();
    this.rebuild_bmd_lines();
    this.build_x_label();
    this.build_y_label();
    this.add_title();
    this.add_legend();
    this.customize_menu();

    var plot = this;
    this.y_axis_label.on("click", function(v){plot.toggle_y_axis();});
    this.x_axis_label.on("click", function(v){plot.toggle_x_axis();});
    this.trigger_resize();
};

DRPlot.prototype.customize_menu = function(){
    this.add_menu();
    if (this.parent){this.parent.add_toggle_button(this);}
    var plot = this;
    var options = {id:'toggle_y_axis',
                   cls: 'btn btn-mini',
                   title: 'Change y-axis scale (shortcut: click the y-axis label)',
                   text: '',
                   icon: 'icon-resize-vertical',
                   on_click: function(){plot.toggle_y_axis();}};
   this.add_menu_button(options);
   options = {id:'toggle_x_axis',
                   cls: 'btn btn-mini',
                   title: 'Change x-axis scale (shortcut: click the x-axis label)',
                   text: '',
                   icon: 'icon-resize-horizontal',
                   on_click: function(){plot.toggle_x_axis();}};
   this.add_menu_button(options);
   if (this.endpoint.data.doses.length>1){
       options = {id: 'toggle_dose_units',
                  cls: 'btn btn-mini',
                  title: 'Change dose-units representation',
                  text: '',
                  icon: 'icon-certificate',
                  on_click: function(){plot.endpoint.toggle_dose_units();}};
       plot.add_menu_button(options);
   }
};

DRPlot.prototype.toggle_y_axis= function(){
    if(window.event && window.event.stopPropagation) event.stopPropagation();
    if(this.endpoint.data.data_type == 'C'){
        if (this.y_axis_settings.scale_type == 'linear'){
            this.y_axis_settings.scale_type = 'log';
            this.y_axis_settings.number_ticks = 1;
            var formatNumber = d3.format(",.f");
            this.y_axis_settings.label_format = formatNumber;
        } else {
            this.y_axis_settings.scale_type = 'linear';
            this.y_axis_settings.number_ticks = 10;
            this.y_axis_settings.label_format = undefined;
        }
    } else {
        var d = this.y_axis_settings.domain;
        if ((d[0]===0) && (d[1]===1)){
            this.y_axis_settings.domain = [this.min_y, this.max_y];
        } else {
            this.y_axis_settings.domain = [0, 1];
        }
    }
    this.y_scale = this._build_scale(this.y_axis_settings);
    this.y_axis_change_chart_update();
};

DRPlot.prototype.toggle_x_axis= function(){
    // get minimum non-zero dose and then set all control doses
    // equal to ten-times lower than the lowest dose
    if(window.event && window.event.stopPropagation) event.stopPropagation();
    if (this.x_axis_settings.scale_type == 'linear'){
        this.x_axis_settings.scale_type = 'log';
        this.x_axis_settings.number_ticks = 1;
        var formatNumber = d3.format(",.f");
        this.x_axis_settings.label_format = formatNumber;
        if(this.endpoint.data.dr[0].dose === 0){
            this.endpoint.data.dr[0].dose = this.endpoint.data.dr[1].dose/10;
            this.endpoint.data.dr[0].dose_original = 0;
        }
        this.min_x = this.endpoint.data.dr[0].dose;
        this.x_axis_settings.domain = [this.min_x/10, this.max_x*(1+this.buff)];
    } else {
        this.x_axis_settings.scale_type = 'linear';
        this.x_axis_settings.number_ticks = 5;
        this.x_axis_settings.label_format = undefined;
        if (this.endpoint.data.dr[0].dose_original !== undefined){
            this.endpoint.data.dr[0].dose = this.endpoint.data.dr[0].dose_original;
        }
        this.min_x = this.endpoint.data.dr[0].dose;
        this.x_axis_settings.domain = [this.min_x-this.max_x*this.buff, this.max_x*(1+this.buff)];
    }
    this.x_scale = this._build_scale(this.x_axis_settings);
    this.x_axis_change_chart_update();
};

DRPlot.prototype.set_defaults = function(){
    // Default settings for a DR plot instance
    this.line_colors = ['#BF3F34', '#545FF2', '#D9B343', '#228C5E', '#B27373']; //bmd lines
    this.padding = {top:40, right:20, bottom:40, left:60};
    this.buff = 0.05; // addition numerical-spacing around dose/response units
    this.radius = 7;
    this.x_axis_settings = {
        'scale_type': this.options.default_y_axis || 'linear',
        'text_orient': "bottom",
        'axis_class': 'axis x_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines x_gridlines',
        'number_ticks': 5,
        'axis_labels':true,
        'label_format':undefined //default
    };

    this.y_axis_settings = {
        'scale_type': this.options.default_x_axis || 'linear',
        'text_orient': "left",
        'axis_class': 'axis y_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines y_gridlines',
        'number_ticks': 6,
        'axis_labels':true,
        'label_format':undefined //default
    };
};

DRPlot.prototype.get_plot_sizes = function(){
    this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
    this.h = this.w; //plot height
    this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
};

DRPlot.prototype.y_axis_change_chart_update = function(){
    // Assuming the plot has already been constructed once,
    // rebuild plot with updated y-scale.
    var y = this.y_scale,
        x = this.x_scale,
        min = y(y.domain()[0]);

    //rebuild y-axis
    this.yAxis
        .scale(y)
        .ticks(this.y_axis_settings.number_ticks,
               this.y_axis_settings.label_format);

    this.vis.selectAll('.y_axis')
        .transition()
        .duration(1000)
        .call(this.yAxis);

    this.rebuild_y_gridlines({animate:true});

    //rebuild error-bars
    this.add_dr_error_bars(true);
    this.add_dose_response(true);
    this.build_bmd_lines();
};

DRPlot.prototype.x_axis_change_chart_update = function(){
    // Assuming the plot has already been constructed once,
    // rebuild plot with updated x-scale.

    var y = this.y_scale,
        x = this.x_scale;

    //rebuild x-axis
    this.xAxis
        .scale(x)
        .ticks(this.x_axis_settings.number_ticks,
               this.x_axis_settings.label_format);

    var svg = this.svg;
    this.vis.selectAll('.x_axis')
        .transition()
        .duration(1000)
        .call(this.xAxis)
        .each("end", function(){
            //force lowest dose on axis to 0
            var vals=[];
            d3.selectAll('.x_axis text').each(function(){vals.push(parseFloat($(this).text()));});
            var min = d3.min(vals).toString();
            min_label = d3.selectAll('.x_axis text').filter(function(){return $(this).text()===min;});
            min_label.text(0);
        });

    this.rebuild_x_gridlines({animate:true});

    this.add_dr_error_bars(true);
    this.add_dose_response(true);
    this.build_bmd_lines();
};

DRPlot.prototype.dr_plot_update = function(){
    // Rebuild the dose-response based on an updated dataset (used with time-dose-response plots).

    this.get_dataset_info();
    this.y_axis_settings.domain = [this.min_y-this.max_y*this.buff, this.max_y*(1+this.buff)];
    this.y_scale = this._build_scale(this.y_axis_settings);

    var y = this.y_scale,
        x = this.x_scale;

    //rebuild y-axis
    this.yAxis
        .scale(y);

    this.vis.selectAll('.y_axis')
        .transition()
        .duration(250)
        .call(this.yAxis);

    this.rebuild_y_gridlines({animate: true, duration: 250});

    //rebuild error-bars
    var opt = {
        data: this.values,
        duration: 250,
        y1:function(d) { return y(d.y_lower);},
        y2:function(d) { return y(d.y_upper);}
    };
    this.build_line(opt, this.error_bars_vertical);

    opt.y2  = function(d) { return y(d.y_lower);};
    this.build_line(opt, this.error_bars_lower);

    $.extend(opt, {
        y1:function(d) { return y(d.y_upper);},
        y2:function(d) { return y(d.y_upper);}});
    this.build_line(opt, this.error_bars_upper);

    //rebuild dose-response-points
    this.dots
        .data(this.values)
        .transition()
        .duration(250)
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    //rebuild title
    this.title_str = this.endpoint.data.name + ' (' + this.endpoint.data.dr[0].time +' hrs)';
    this.add_title();
};

DRPlot.prototype.get_dataset_info = function(){
    this.title_str = this.endpoint.data.name;
    this.x_label_text = "Dose ({0})".printf(this.endpoint.data.dose_units);
    this.y_label_text = "Response ({0})".printf(this.endpoint.data.response_units);

    // Get values to be used in dose-response plots
    var ep = this.endpoint.data,
        values = [],
        sigs_data = [],
        self = this;

    $(this.endpoint.data.dr).each(function(i, v){
        var value = {'x': v.dose, 'cls': 'dose_points',
                     'y_lower':v.lower_limit, 'y_upper':v.upper_limit},
            txt = ["Dose = {0} {1}".printf(v.dose, ep.dose_units),
                   "N = {0}".printf(v.n)];
        if (ep.data_type =='C'){
            value.y = v.response;
            txt.push("Response = {0} {1}".printf(v.response, ep.response_units),
                     "{0} = {1}".printf(ep.variance_name, v.variance));
        } else {
            value.y = v.incidence/v.n;
            txt.push("Incidence = {0} {1}".printf(v.incidence, ep.response_units));
        }
        if (ep.LOAEL == i){value.cls = value.cls + ' LOAEL'; }
        if (ep.NOAEL == i){value.cls = value.cls + ' NOAEL'; }

        if (v.significance_level>0){
            sigs_data.push({'x': v.dose,
                            'significance_level': v.significance_level,
                            'y': v.upper_limit});
        }

        value.txt = txt.join('\n');
        values.push(value);
    });
    this.values = values;
    this.sigs_data = sigs_data;

    // get plot domain
    this.min_x = d3.min(this.endpoint.data.dr, function(datum) { return datum.dose; });
    this.max_x = d3.max(this.endpoint.data.dr, function(datum) { return datum.dose; });

    if (this.endpoint.data.dr.length>0){
        var max_upper = d3.max(values, function(d){return d.y_upper;}),
            max_sig = d3.max(sigs_data, function(d){return d.y;});

        this.min_y = d3.min(this.endpoint.data.dr, function(datum){return datum.lower_limit;});
        this.max_y = d3.max([max_upper, max_sig]);
    }
};

DRPlot.prototype.add_axes = function() {
    // customizations for axis updates

    $.extend(this.x_axis_settings, {
        'domain': [this.min_x-this.max_x*this.buff, this.max_x*(1+this.buff)],
        'rangeRound': [0, this.w],
        'x_translate': 0,
        'y_translate': this.h
    });

    $.extend(this.y_axis_settings, {
        'domain': [this.min_y-this.max_y*this.buff, this.max_y*(1+this.buff)],
        'rangeRound': [this.h, 0],
        'x_translate': 0,
        'y_translate': 0
    });

    this.build_x_axis();
    this.build_y_axis();
};

DRPlot.prototype.add_selected_endpoint_BMD = function(){
    // Update BMD lines based on dose-changes
    var self = this;
    if ((this.endpoint.data.BMD) &&
        (this.endpoint.data.BMD.dose_units_id === this.endpoint.data.dose_units_id)){
        var append = true;
        self.bmd.forEach(function(v, i){
            if (v.BMD.id === self.endpoint.data.BMD.id){append = false;}
        });
        if (append){this.add_bmd_line(this.endpoint.data.BMD, 'd3_bmd_selected');}
    }
};

DRPlot.prototype.add_dr_error_bars = function(update){
    var x = this.x_scale,
        y = this.y_scale,
        hline_width = x.range()[1] * 0.02;
    this.hline_width = hline_width;

    try{
        if (!update){
            delete this.error_bars_vertical;
            delete this.error_bars_upper;
            delete this.error_bars_lower;
            delete this.error_bar_group;
        }
    } catch (err){}

    if (!this.error_bar_group){
        this.error_bar_group = this.vis.append("g")
            .attr('class','error_bars');
    }

    var bar_options = {
        data: this.values,
        x1: function(d) {return x(d.x);},
        y1: function(d) {return y(d.y_lower);},
        x2: function(d) {return x(d.x);},
        y2: function(d) {return y(d.y_upper);},
        classes: 'dr_err_bars',
        append_to: this.error_bar_group
    };

    if (this.error_bars_vertical && update){
        this.error_bars_vertical = this.build_line(bar_options, this.error_bars_vertical);
    } else {
        this.error_bars_vertical = this.build_line(bar_options);
    }

    $.extend(bar_options, {
        x1: function(d,i) {return x(d.x) + hline_width;},
        y1: function(d) {return y(d.y_lower);},
        x2: function(d,i) {return x(d.x) - hline_width;},
        y2: function(d) {return y(d.y_lower);}
    });
    if (this.error_bars_lower && update){
        this.error_bars_lower = this.build_line(bar_options, this.error_bars_lower);
    } else {
        this.error_bars_lower = this.build_line(bar_options);
    }

    $.extend(bar_options, {
        y1: function(d) {return y(d.y_upper);},
        y2: function(d) {return y(d.y_upper);}});
    if (this.error_bars_upper && update){
        this.error_bars_upper = this.build_line(bar_options, this.error_bars_upper);
    } else {
        this.error_bars_upper = this.build_line(bar_options);
    }
};

DRPlot.prototype.add_dose_response = function(update) {
    // update or create dose-response dots and labels
    var x = this.x_scale,
        y = this.y_scale;

    if (this.dots && update){
        this.dots
            .data(this.values)
            .transition()
            .duration(1000)
            .attr("transform", function(d) {
                    return "translate(" + x(d.x)  + "," +
                            y(d.y) + ")"; });

        this.sigs
            .data(this.sigs_data)
            .transition()
            .duration(1000)
            .attr("x", function(d){return x(d.x);})
            .attr("y", function(d){return y(d.y);});

    } else {
        var dots_group = this.vis.append("g")
                .attr('class','dr_dots');
        this.dots = dots_group.selectAll("path.dot")
            .data(this.values)
        .enter().append("circle")
            .attr("r", this.radius)
            .attr("class", function(d) {return d.cls;})
            .attr("transform", function(d) {
                    return "translate(" + x(d.x) + "," +
                            y(d.y) + ")"; });

        this.dot_labels = this.dots.append("svg:title")
                            .text(function(d) { return d.txt; });

        var sigs_group = this.vis.append("g");

        this.sigs = sigs_group.selectAll("text")
                .data(this.sigs_data)
            .enter().append("svg:text")
                .attr("x", function(d){return x(d.x);})
                .attr("y", function(d){return y(d.y);})
                .attr("text-anchor", "middle")
                .style({"font-size": "18px",
                        "font-weight": "bold",
                        "cursor": "pointer"})
                .text("*");

        this.sigs_labels = this.sigs.append("svg:title")
                            .text(function(d) { return 'Statistically significant at {0}'.printf(d.significance_level); });
    }
};

DRPlot.prototype.clear_legend = function(){
    //remove existing legend
    $($(this.legend)[0]).remove();
    $(this.plot_div.find('.legend_circle')).remove();
    $(this.plot_div.find('.legend_text')).remove();
};

DRPlot.prototype.add_legend = function(){
    // clear any existing legends
    this.clear_legend();

    var legend_settings = {};
    legend_settings.items = [{'text':'Doses in Study', 'classes':'dose_points', 'color':undefined}];
    if (this.plot_div.find('.LOAEL').length > 0) { legend_settings.items.push({'text':'LOAEL', 'classes':'LOAEL', 'color':undefined}); }
    if (this.plot_div.find('.NOAEL').length > 0) { legend_settings.items.push({'text':'NOAEL', 'classes':'NOAEL', 'color':undefined}); }
    $.each($(this.bmd), function(i, v){
        legend_settings.items.push({'text': this.BMD.model_name, 'classes': '', 'color': this.line_color });
    });

    legend_settings.item_height = 20;
    legend_settings.box_w = 110;
    legend_settings.box_h = legend_settings.items.length*legend_settings.item_height;

    legend_settings.box_padding = 5;
    legend_settings.dot_r = 5;

    if (this.legend_left){
        legend_settings.box_l = this.legend_left;
    } else {
        legend_settings.box_l = this.w - legend_settings.box_w-10;
    }

    if (this.legend_top){
        legend_settings.box_t = this.legend_top;
    } else if (this.endpoint.data.dataset_increasing) {
        legend_settings.box_t = this.h-legend_settings.box_h - 20;
    } else {
        legend_settings.box_t = 10;
    }


    //add final rectangle around plot
    this.add_final_rectangle();

    // build legend
    this.build_legend(legend_settings);
};

DRPlot.prototype.clear_bmd_lines = function(line_class){
    // reclaim the color to be used again in the future
    if (line_class === undefined){line_class = 'd3_bmd_clicked';}

    // use a reverse-for loop so it won't skip indices when deleted
    if(this.bmd.length>=1){
        for (var i = this.bmd.length - 1; i >= 0; i -= 1) {
            if (this.bmd[i].line_class == line_class){
                this.line_colors.push(this.bmd[i].line_color); // reclaim color
                this.bmd[i].remove_line_group(); // remove lines
                this.bmd.splice(i,1);   // remove from array
            }
        }
    }

    this.add_legend();
};

DRPlot.prototype.cleanup_before_change = function(){
    this.bmd.forEach(function(v){
        v.remove_line_group();
    });
};

DRPlot.prototype.build_bmd_lines = function(){
    // build any bmd lines to ensure they're persistent on graph
    this.bmd.forEach(function(v, i){
        v.construct_line();
    });
};

DRPlot.prototype.rebuild_bmd_lines = function(){
    // rebuild any bmd lines to ensure they're persistent on graph
    this.bmd.forEach(function(v, i){
        v.remove_line_group();
        v.construct_line();
    });
};

DRPlot.prototype.add_bmd_line = function(BMD, line_class){
    // Add a BMD line to a DRPlot, using one of three line classess specified:
    // 1) d3_bmd_hover
    // 2) d3_bmd_clicked
    // 3) d3_bmd_selected

    if (line_class === undefined){line_class = 'd3_bmd_clicked';}
    line = new BMDline(this, BMD, line_class);
    this.bmd.push(line);
    this.add_legend();
};


var BMDline = function(DRPlot, BMD, line_class){
    this.DRPlot = DRPlot;
    this.BMD = BMD;
    this.line_class = line_class;
    this.line_color = DRPlot.line_colors.splice(0,1)[0];
    this.construct_line();
};

BMDline.prototype.remove_line_group = function(){
    if (this.line_group){
        this.bmd_line.remove();
        this.bmr_lines.remove();
        this.line_group.remove();
        delete this.bmd_line;
        delete this.bmr_lines;
        delete this.line_group;
    }
};

BMDline.prototype.construct_line = function(){

    // build BMD-line estimate of the dose-range
    var x = this.DRPlot.x_scale,
        y = this.DRPlot.y_scale,
        x_domain = x.domain(),
        min_x;

    // Construct BMD model-form
    var modelform = this.BMD.plotting.formula;
    $.each(this.BMD.plotting.parameters, function(k, v){
       k = k.replace('(','\\(').replace(')','\\)'); // escape parenthesis (multistage models)
       var re = new RegExp("{" + k +"}", "g");
       modelform = modelform.replace(re, v);
    });
    this.modelform = modelform;

    // determine minimum x to model
    if (($.inArray(this.DRPlot.endpoint.data.data_type, ["D", "DC"]) >= 0) ||
        ($.inArray(this.BMD.model_name, ["Exponential-M3", "Hill", "Power"]) >= 0)) {
        min_x = 1e-10; // zero can cause problems
    } else {
        min_x = x_domain[0];
    }
    if (this.DRPlot.x_axis_settings.scale_type === "log"){
        min_x = 1e-10;
    }

    // Build line group
    this.line_group = this.DRPlot.vis.append("g")
                        .attr('class', (this.line_class + ' bmd_line'))
                        .style('stroke', this.line_color);

    // Build BMD lines
    var values = d3.range(min_x, x_domain[1], x_domain[1]/100.0)
        .map(function(x){
            var val = eval(modelform);
            val = (isNaN(val)) ? y.domain()[0] : val;
            return {x1: x, y1:val};});

    // add line to plot
    var line_function = d3.svg.line()
                .interpolate("basis")
                .x(function(d) { return x(d.x1); })
                .y(function(d) { return y(d.y1); });

    if (this.bmd_line){
        this.bmd_line
            .transition()
            .duration(1000)
            .attr("d", line_function(values));
    } else {
        this.bmd_line = this.line_group.append("svg:path")
                            .attr("d", line_function(values));
    }

    // add BMD, BMDL, and BMR lines
    if ('BMD' in this.BMD.outputs){
        var model = this.modelform,
            within_range = function(value, range){
                return ((value >= range[0]) &&( value <= range[1]));
            },
            func = function(x){return eval(model);},
            bmr = func(this.BMD.outputs.BMD),
            options = {
                append_to: this.line_group,
                data: [],
                x1: function(d) {return x(d.x1);},
                x2: function(d) {return x(d.x2);},
                y1: function(d) {return y(d.y1);},
                y2: function(d) {return y(d.y2);}
            };

        if (within_range(bmr, y.domain())){
            options.data.push({x1: x.domain()[0],
                               x2: d3.min([this.BMD.outputs.BMD, x.domain()[1]]),
                               y1: bmr,
                               y2: bmr});
        }

        if (within_range(this.BMD.outputs.BMD, x.domain())){
            options.data.push({x1: this.BMD.outputs.BMD,
                               x2: this.BMD.outputs.BMD,
                               y1: y.domain()[0],
                               y2: d3.min([bmr, y.domain()[1]])});
       }

        if (within_range(this.BMD.outputs.BMDL, x.domain())){
            options.data.push({x1: this.BMD.outputs.BMDL,
                               x2: this.BMD.outputs.BMDL,
                               y1: y.domain()[0],
                               y2: d3.min([bmr, y.domain()[1]])});
        }

        if (this.bmr_lines){
            this.bmr_lines = this.DRPlot.build_line(options, this.bmr_lines);
        } else {
            this.bmr_lines = this.DRPlot.build_line(options);
        }
    }
};


Barplot = function(endpoint, plot_id, options, parent){
    D3Plot.call(this); // call parent constructor
    this.parent = parent;
    this.endpoint = endpoint;
    this.plot_div = $(plot_id);
    this.options = options || {build_plot_startup:true};
    this.set_defaults();
    this.get_dataset_info();
    this.endpoint.addObserver(this);
    if (this.options.build_plot_startup){this.build_plot();}
};

Barplot.prototype = new D3Plot();
Barplot.prototype.constructor = Barplot;

Barplot.prototype.build_plot = function(){
    this.plot_div.html('');
    this.get_plot_sizes();
    this.build_plot_skeleton(true);
    this.add_title();
    this.add_axes();
    this.add_bars();
    this.add_error_bars();
    this.build_x_label();
    this.build_y_label();
    this.add_final_rectangle();
    this.add_legend();
    this.customize_menu();

    var plot = this;
    this.y_axis_label.on("click", function(v){plot.toggle_y_axis();});
    this.trigger_resize();
};

Barplot.prototype.customize_menu = function(){
    this.add_menu();
    if (this.parent){this.parent.add_toggle_button(this);}
    var plot = this;
    var options = {id:'toggle_y_axis',
                   cls: 'btn btn-mini',
                   title: 'Change y-axis scale (shortcut: click the y-axis label)',
                   text: '',
                   icon: 'icon-resize-vertical',
                   on_click: function(){plot.toggle_y_axis();}};
   plot.add_menu_button(options);

   if (this.endpoint.data.doses.length>1){
       options = {id: 'toggle_dose_units',
                  cls: 'btn btn-mini',
                  title: 'Change dose-units representation',
                  text: '',
                  icon: 'icon-certificate',
                  on_click: function(){plot.endpoint.toggle_dose_units();}};
       plot.add_menu_button(options);
   }
};

Barplot.prototype.toggle_y_axis = function(){
    if (this.endpoint.data.data_type == 'C'){
        if (this.y_axis_settings.scale_type == 'linear'){
            this.y_axis_settings.scale_type = 'log';
            this.y_axis_settings.number_ticks = 1;
            var formatNumber = d3.format(",.f"),
            formatLog = function(d) { return formatNumber(d); };
            this.y_axis_settings.label_format = formatNumber;

        } else {
            this.y_axis_settings.scale_type = 'linear';
            this.y_axis_settings.number_ticks = 10;
            this.y_axis_settings.label_format = undefined;
        }
    } else {
        var d = this.y_axis_settings.domain;
        if ((d[0]===0) && (d[1]===1)){
            this.y_axis_settings.domain = [this.min_y, this.max_y];
        } else {
            this.y_axis_settings.domain = [0, 1];
        }
    }
    this.y_scale = this._build_scale(this.y_axis_settings);
    this.y_axis_change_chart_update();
};

Barplot.prototype.update = function(status){
    if (status.status === "dose_changed"){
        this.dose_scale_change();
    }
};

Barplot.prototype.dose_scale_change = function(){
    this.get_dataset_info();
    if (this.parent && this.parent.plot === this){
        this.x_axis_settings.domain = this.endpoint.data.dr.map(
                function(d){return String(d.dose);});
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.x_axis_change_chart_update();
        this.build_x_label();
    }
};

Barplot.prototype.set_defaults = function(){
    // Default settings
    this.padding = {top:40, right:20, bottom:40, left:60};
    this.buff = 0.05; // addition numerical-spacing around dose/response units

    this.x_axis_settings = {
        'scale_type': 'ordinal',
        'text_orient': "bottom",
        'axis_class': 'axis x_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines x_gridlines',
        'axis_labels':true,
        'label_format':undefined //default
    };

    this.y_axis_settings = {
        'scale_type': this.options.default_y_axis || 'linear',
        'text_orient': "left",
        'axis_class': 'axis y_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines y_gridlines',
        'number_ticks': 10,
        'axis_labels':true,
        'label_format':undefined //default
    };
};

Barplot.prototype.get_plot_sizes = function(){
    this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
    this.h = this.w; //plot height
    this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
};

Barplot.prototype.get_dataset_info = function(){

    this.get_plot_sizes();
    // space lines in half-increments
    var min = Infinity, max = -Infinity, val, txt, cls, e,
        default_y_scale = this.default_y_scale,
        values = [],
        sigs_data = [];

    e = this.endpoint;
    $(this.endpoint.data.dr).each(function(i, v){
        if(e.data.data_type=='C'){
            val = v.response;
            txt = v.response;
        } else{
            val = v.incidence/v.n;
            txt = val;
        }

        cls='dose_bars';
        if(e.data.NOAEL == i){cls+=' NOAEL';}
        if(e.data.LOAEL == i){cls+=' LOAEL';}

        values.push({'dose': v.dose,
                     'value':val,
                     'high':v.upper_limit,
                     'low':v.lower_limit,
                     'txt':txt,
                     'classes':cls});
        min = Math.min(min, v.lower_limit, val);
        max = Math.max(max, v.upper_limit);

        if (v.significance_level>0){
            sigs_data.push({'x': v.dose,
                            'significance_level': v.significance_level,
                            'y': v.upper_limit});
        }

    });
    this.values = values;
    this.sigs_data = sigs_data;

    if(this.endpoint.data.data_type=='C'){
        min = min - (max*this.buff);
    } else {
        min = 0;
    }
    max = max*(1+this.buff);

    if (this.default_y_scale == "log"){
        this.min_y = Math.pow(10, Math.floor(Math.log10(min)));
        this.max_y = Math.pow(10, Math.ceil(Math.log10(max)));
    } else {
        this.min_y = min;
        this.max_y = max;
    }

    this.title_str = this.endpoint.data.name;
    this.x_label_text = "Doses ({0})".printf(this.endpoint.data.dose_units);
    this.y_label_text = "Response ({0})".printf(this.endpoint.data.response_units);
};

Barplot.prototype.add_axes = function() {
    $.extend(this.x_axis_settings, {
        domain: this.endpoint.data.dr.map(function(d){return String(d.dose);}),
        number_ticks: this.endpoint.data.dr.length,
        rangeRound: [0, this.w],
        x_translate: 0,
        y_translate: this.h
    });

    $.extend(this.y_axis_settings, {
        domain: [this.min_y, this.max_y],
        rangeRound: [this.h, 0],
        x_translate: 0,
        y_translate: 0
    });

    this.build_x_axis();
    this.build_y_axis();
};

Barplot.prototype.add_bars = function(){
    var x = this.x_scale,
        y = this.y_scale,
        bar_spacing = 0.1,
        bar_offset = x.rangeBand()*bar_spacing,
        min = y(y.domain()[0]);

    this.dose_bar_group = this.vis.append("g");
    this.bars = this.dose_bar_group.selectAll("svg.bars")
        .data(this.values)
      .enter().append("rect")
        .attr("x", function(d,i) { return x(d.dose)+x.rangeBand()*bar_spacing; })
        .attr("y", function(d,i) { return y(d.value); } )
        .attr("width", x.rangeBand()*(1-2*bar_spacing))
        .attr("height", function(d) { return min - y(d.value); })
        .attr('class', function(d) {return d.classes;});

    this.bars.append("svg:title").text(function(d) {return d.txt;});

    var sigs_group = this.vis.append("g");
    this.sigs = sigs_group.selectAll("text")
            .data(this.sigs_data)
        .enter().append("svg:text")
            .attr("x", function(d){return x(d.x)+x.rangeBand()/2;})
            .attr("y", function(d){return y(d.y);})
            .attr("text-anchor", "middle")
            .style({"font-size": "18px",
                    "font-weight": "bold",
                    "cursor": "pointer"})
            .text("*");

    this.sigs_labels = this.sigs.append("svg:title")
            .text(function(d) { return 'Statistically significant at {0}'.printf(d.significance_level); });
};

Barplot.prototype.x_axis_change_chart_update = function(){
    this.xAxis.scale(this.x_scale);
    this.vis.selectAll('.x_axis')
        .transition()
        .call(this.xAxis);
};

Barplot.prototype.y_axis_change_chart_update = function(){
    // Assuming the plot has already been constructed once,
    // rebuild plot with updated y-scale.

    var y = this.y_scale,
        min = y(y.domain()[0]);

    //rebuild y-axis
    this.yAxis
        .scale(y)
        .ticks(this.y_axis_settings.number_ticks,
               this.y_axis_settings.label_format);

    this.vis.selectAll('.y_axis')
        .transition()
        .duration(1000)
        .call(this.yAxis);

    this.rebuild_y_gridlines({animate:true});

    //rebuild error-bars
    var opt = {
        y1:function(d) { return y(d.low);},
        y2:function(d) { return y(d.high);}
    };
    this.build_line(opt, this.error_bars_vertical);

    opt.y2  = function(d) { return y(d.low);};
    this.build_line(opt, this.error_bars_lower);

    opt = {
        y1:function(d) { return y(d.high);},
        y2:function(d) { return y(d.high);}
    };
    this.build_line(opt, this.error_bars_upper);

    //rebuild dose-bars
    this.bars
        .transition()
        .duration(1000)
        .attr("y", function(d,i){return y(d.value);})
        .attr("height", function(d){ return min - y(d.value); });

    this.sigs
        .transition()
        .duration(1000)
        .attr("y", function(d){return y(d.y);});
};

Barplot.prototype.add_error_bars = function(){
    var hline_width = this.w * 0.02,
        x = this.x_scale,
        y = this.y_scale;

    this.error_bar_group = this.vis.append("g")
            .attr('class','error_bars');

    bar_options = {
        data: this.values,
        x1: function(d) {return x(d.dose)+x.rangeBand()/2;},
        y1: function(d) {return y(d.low);},
        x2: function(d) {return x(d.dose)+x.rangeBand()/2;},
        y2: function(d) {return y(d.high);},
        classes: 'dr_err_bars',
        append_to: this.error_bar_group
    };
    this.error_bars_vertical = this.build_line(bar_options);

    $.extend(bar_options, {
        x1: function(d,i) {return x(d.dose) + x.rangeBand()/2 - hline_width;},
        y1: function(d) {return y(d.low);},
        x2: function(d,i) {return x(d.dose) + x.rangeBand()/2 + hline_width;},
        y2: function(d) {return y(d.low);}
    });
    this.error_bars_lower = this.build_line(bar_options);

    $.extend(bar_options, {
        y1: function(d) {return y(d.high);},
        y2: function(d) {return y(d.high);}});
    this.error_bars_upper = this.build_line(bar_options);
};

Barplot.prototype.add_legend = function(){
    var legend_settings = {};
    legend_settings.items = [{'text':'Doses in Study', 'classes':'dose_points', 'color':undefined}];
    if (this.plot_div.find('.LOAEL').length > 0) { legend_settings.items.push({'text':'LOAEL', 'classes':'LOAEL', 'color':undefined}); }
    if (this.plot_div.find('.NOAEL').length > 0) { legend_settings.items.push({'text':'NOAEL', 'classes':'NOAEL', 'color':undefined}); }
    if (this.plot_div.find('.BMDL').length > 0) { legend_settings.items.push({'text':'BMDL', 'classes':'BMDL', 'color':undefined}); }
    legend_settings.item_height = 20;
    legend_settings.box_w = 110;
    legend_settings.box_h = legend_settings.items.length*legend_settings.item_height;
    legend_settings.box_padding = 5;
    legend_settings.dot_r = 5;

    if (this.legend_left){
        legend_settings.box_l = this.legend_left;
    } else {
        legend_settings.box_l = 10;
    }

    if (this.legend_top){
        legend_settings.box_t = this.legend_top;
    } else {
        legend_settings.box_t = 10;
    }

    this.build_legend(legend_settings);
};

Barplot.prototype.cleanup_before_change = function(){};


BWPlot = function(endpoint, div, options, parent){
    /*
     * Box and whisker's plot used to represent individual animal data.
     */
    D3Plot.call(this); // call parent constructor
    this.parent = parent;
    this.endpoint = endpoint;
    this.plot_div = $(div);
    this.options = options || {build_plot_startup:true};
    this.set_defaults();
    this.get_dataset_info();
    if (this.options.build_plot_startup){this.build_plot();}
};

BWPlot.prototype = new D3Plot();
BWPlot.prototype.constructor = BWPlot;

BWPlot.prototype.build_plot = function(){
    this.plot_div.empty();
    this.get_plot_sizes();
    this.build_plot_skeleton(true);
    this.add_title();
    this.add_axes();
    this.build_boxplot();
    this.build_x_label();
    this.build_y_label();
    this.add_final_rectangle();
    this.customize_menu();

    this.filter_mode = false;
    var plot = this;
    $('body').on('keydown', function() {
        if (event.ctrlKey || event.metaKey){plot.filter_y_axis();}
    });
    this.trigger_resize();
};

BWPlot.prototype.customize_menu = function(){
    this.add_menu();
    if (this.parent){this.parent.add_toggle_button(this);}
    var plot = this;
    var options = {id:'filter_response',
                   cls: 'btn btn-mini',
                   title: 'Filter response (shortcut: press ctrl to toggle)',
                   text: '',
                   icon: 'icon-filter',
                   on_click: function(){plot.filter_y_axis();}};
   plot.add_menu_button(options);
};

BWPlot.prototype.filter_y_axis = function(){
    var plot = this;
    $('#filter_response').toggleClass("btn-info");
    this.filter_mode = !this.filter_mode;
    if (this.filter_mode) {
        this.bounding_rectangle
            .attr('class', 'bounding_rectangle bounding_rectangle_cover')
            .on('mousemove', function(){plot.add_reference_line(this);});
    } else {
        this.bounding_rectangle
            .attr('class', 'bounding_rectangle')
            .on('mousemove', undefined);
    }
};

BWPlot.prototype.set_defaults = function(){
    // Default settings
    this.padding = {top:40, right:20, bottom:40, left:60};
    this.buff = 0.05; // addition numerical-spacing around dose/response units

    this.x_axis_settings = {
        'scale_type': 'ordinal',
        'text_orient': "bottom",
        'axis_class': 'axis x_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines x_gridlines',
        'axis_labels':true,
        'label_format':undefined //default
    };

    this.y_axis_settings = {
        'scale_type': this.options.default_y_axis || 'linear',
        'text_orient': "left",
        'axis_class': 'axis y_axis',
        'gridlines': true,
        'gridline_class': 'primary_gridlines y_gridlines',
        'number_ticks': 10,
        'axis_labels':true,
        'label_format':undefined //default
    };
};

BWPlot.prototype.get_plot_sizes = function(){
    this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
    this.h = this.w; //plot height
    this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
};

BWPlot.prototype.add_reference_line = function(event){

    this.dots.attr('class', 'data_point');
    // check if in domain before continuing
    if (!this.isWithinDomain(event)){
        if (this.reference_line){
           this.reference_line.remove();
           this.reference_text.remove();
           delete this.reference_line;
           delete this.reference_text;
       }
       return;
    }

    var y_value = d3.mouse(event)[1],
        threshold = this.y_scale.invert(y_value);

    var txt = [], x = this.x_scale;
    this.endpoint.data.dr.forEach(function(v, i){
        var exceed = v.individual_responses.filter(function(e){return e>threshold;}).length;
        txt.push({'x':i+1, 'txt': exceed + '/' + v.individual_responses.length + ' (' + Math.round(exceed/v.individual_responses.length*100,2) +'%)'});
    });

    // filter dots
    this.dots.attr('class', 'data_point');
    this.dots.filter(function(d){return d.y>threshold;})
            .attr('class','data_point_above');

    // add reference lines
    if (this.reference_line){
        this.reference_line
            .transition()
            .duration(10)
            .attr("y1", y_value)
            .attr("y2", y_value);
    } else {
        this.reference_line = this.vis.append("line")
            .attr("x1", 0)
            .attr("y1", y_value)
            .attr("x2", this.w)
            .attr("y2", y_value)
            .attr('class','reference_line');
    }

    // add summary stats text fields
    if (this.reference_text){
        this.reference_text
            .data(txt)
            .transition()
            .duration(10)
            .text(function(d,i) { return d.txt; });
    } else {
        this.reference_text = this.vis.selectAll("text.reference_text")
            .data(txt)
            .enter().append("svg:text")
            .attr("x", function(d,i) {return x(d.x)+x.rangeBand()/2;})
            .attr("y", function(d,i) {return 15;})
            .attr("class", "reference_text")
            .text(function(d,i) {return d.txt;});
    }
};

BWPlot.prototype.get_dataset_info = function(){
    var y_min = Infinity, y_max = -Infinity,
        values = [], stats = [], bars = [];

    this.endpoint.data.dr.forEach(function(v, i){
        var stat = {x: v.dose,
                    min: d3.min(v.individual_responses),
                    five: v.response - 1.645*v.stdev,
                    twentyfive: v.response - 0.685*v.stdev,
                    fifty: v.response,
                    seventyfive: v.response + 0.685*v.stdev,
                    ninetyfive: v.response + 1.645*v.stdev,
                    max: d3.max(v.individual_responses)};
        y_min = Math.min(y_min, d3.min(v.individual_responses));
        y_max = Math.max(y_max, d3.max(v.individual_responses));
        stats.push(stat);
        var txt = '5th: ' + stat.five +
                  '\n25th: ' + stat.twentyfive +
                  '\n50th: ' + stat.fifty +
                  '\n75th: ' + stat.seventyfive +
                  '\n95th: ' + stat.ninetyfive;
        bars.push({x: v.dose, y_low: stat.twentyfive, y_high: stat.fifty, classes: 'dose_points', 'txt':txt});
        bars.push({x: v.dose, y_low: stat.fifty, y_high: stat.seventyfive, classes: 'dose_points', 'txt':txt});

        v.individual_responses.forEach(function(v2, i2){
            values.push({'x': v.dose,
                         'y': v2,
                         'txt':'Value: ' + v2,
                         'classes': 'dose_points'});
        });
    });

    this.min_y = d3.min([y_min, 0]);
    this.max_y = y_max*(1+this.buff);
    this.bars_data = bars;
    this.values = values;
    this.stats = stats;

    this.title_str = this.endpoint.data.name;
    this.x_label_text = "Doses ({0})".printf(this.endpoint.data.dose_units);
    this.y_label_text = "Response ({0})".printf(this.endpoint.data.response_units);
};

BWPlot.prototype.add_axes = function() {
    $.extend(this.x_axis_settings, {
        domain: this.endpoint.data.dr.map(function(d){return String(d.dose);}),
        number_ticks: this.endpoint.data.dr.length,
        rangeRound: [0, this.w],
        x_translate: 0,
        y_translate: this.h
    });

    $.extend(this.y_axis_settings, {
        domain: [this.min_y, this.max_y],
        rangeRound: [this.h, 0],
        x_translate: 0,
        y_translate: 0
    });

    this.build_x_axis();
    this.build_y_axis();
};

BWPlot.prototype.build_boxplot = function(){
    var hline_width = this.w * 0.02,
        x = this.x_scale,
        y = this.y_scale,
        bar_spacing = 0.1,
        bar_offset = x.rangeBand()*bar_spacing;

    // create groups
    this.boxplots = this.vis.append("g").attr('class', 'boxplots');
    this.dots_group = this.vis.append("g");

    // Add rectangles
    this.bars = this.boxplots.selectAll("svg.bars")
        .data(this.bars_data)
      .enter().append("rect")
        .attr("x", function(d,i) { return x(d.x)+bar_offset; })
        .attr("y", function(d,i) { return y(d.y_high); } )
        .attr("width", x.rangeBand()*(1-2*bar_spacing))
        .attr("height", function(d) { return y(d.y_low)-y(d.y_high); })
        .attr('class', function(d) {return d.classes;})
        .attr('opacity', 0.7);

    this.bars.append("svg:title")
        .text(function(d) { return d.txt; });

    // Add lines
    bar_options = {
        data: this.stats,
        x1: function(d) {return x(d.x)+x.rangeBand()/2;},
        y1: function(d) {return y(d.five);},
        x2: function(d) {return x(d.x)+x.rangeBand()/2;},
        y2: function(d) {return y(d.twentyfive);},
        classes: 'dr_err_bars dr_err_bars_v',
        append_to: this.boxplots
    };
    this.lower_vertical = this.build_line(bar_options);

    $.extend(bar_options, {
        y1: function(d) {return y(d.seventyfive);},
        y2: function(d) {return y(d.ninetyfive);}});
    this.upper_vertical = this.build_line(bar_options);

    $.extend(bar_options, {
        x1: function(d) {return x(d.x) + x.rangeBand()*bar_spacing;},
        y1: function(d) {return y(d.five);},
        x2: function(d) {return x(d.x) + x.rangeBand()*(1-bar_spacing);},
        y2: function(d) {return y(d.five);}
    });
    this.lower_horizontal = this.build_line(bar_options);

    $.extend(bar_options, {
        y1: function(d) {return y(d.ninetyfive);},
        y2: function(d) {return y(d.ninetyfive);}});
    this.upper_horizontal = this.build_line(bar_options);

    // add dots
    this.dots = this.dots_group.selectAll("path.dot")
        .data(this.values)
    .enter().append("circle")
        .attr("r", "3")
        .attr("class", "data_point")
        .attr("transform", function(d) { return "translate(" +
            (x(d.x)+x.rangeBand()/2 + (Math.random()-0.5)*(0.5*x.rangeBand())) +
            "," + y(d.y) + ")"; });

    this.dots.append("svg:title")
        .text(function(d) { return d.txt; });
};

BWPlot.prototype.add_bmd_line = function(){};

BWPlot.prototype.cleanup_before_change = function(){};
