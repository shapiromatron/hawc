var EndpointCriticalDose = function(endpoint, span, type, show_units){
    // custom field to observe dose changes and respond based on selected dose
    endpoint.addObserver(this);
    this.endpoint = endpoint;
    this.span = span;
    this.type = type;
    this.critical_effect_idx = endpoint.data[type];
    this.show_units = show_units;
    this.display();
};
EndpointCriticalDose.prototype = {
    display: function(){
        var txt = "",
            self = this,
            doses = this.endpoint.doses.filter(function(v){
                return v.name === self.endpoint.dose_units;});
        try {
            txt = doses[0].values[this.critical_effect_idx].dose.toHawcString();
            if (this.show_units) txt = "{0} {1}".printf(txt, this.endpoint.dose_units);
        } catch(err){}
        this.span.html(txt);
    },
    update: function(){
        this.display();
    },
};


var BMDResult = function(endpoint, span, type, show_units, show_url){
    this.show_url = show_url;
    EndpointCriticalDose.apply(this, arguments);
};
_.extend(BMDResult.prototype, EndpointCriticalDose.prototype, {
    display: function(){
        var txt,
            bmd = this.endpoint.data.bmd,
            currentUnits = this.endpoint.dose_units_id,
            bmdUnits = this.endpoint.data.bmd.dose_units;

        if (currentUnits == bmdUnits){
            txt = bmd.output[this.type].toHawcString();
            if (this.show_units){
                txt = txt + ' {0}'.printf(this.endpoint.dose_units);
            }
            if (this.show_url){
                txt = txt + ' <a href="{0}">(view details)</a>'.printf(bmd.url);
            }
        } else {
            txt = '-';
        }
        return this.span.html(txt);
    },
});


var EndpointPlotContainer = function(endpoint, plot_id){
    //container used for endpoint plot organization
    this.endpoint = endpoint;
    this.plot_div = $(plot_id);
    this.plot_id = plot_id;

    if(!this.endpoint.hasEGdata()){
        this.plot_div.html('<p>Plot unavailable.</p>');
    } else {
        var options = {'build_plot_startup':false};
        this.plot_style = [
            new Barplot(endpoint, this.plot_id, options, this),
            new DRPlot(endpoint, this.plot_id, options, this)
        ];
        this.toggle_views();
    }
};
EndpointPlotContainer.prototype = {
    add_bmd_line: function(selected_model, line_class){
        if (this.plot.add_bmd_line){
            this.plot.add_bmd_line(selected_model, line_class);
        }
    },
    toggle_views: function(){
        // change the current plot style
        if (this.plot){this.plot.cleanup_before_change();}
        this.plot_style.unshift(this.plot_style.pop());
        this.plot = this.plot_style[0];
        this.plot.build_plot();
    },
    add_toggle_button: function(plot){
        // add toggle to menu options to view other ways
        var ep = this;
        var options = {id:'plot_toggle',
                       cls: 'btn btn-mini',
                       title: 'View alternate visualizations',
                       text: '',
                       icon: 'icon-circle-arrow-right',
                       on_click: function(){ep.toggle_views();}};
       plot.add_menu_button(options);
    }
};


var EndpointTable = function(endpoint, tbl_id){
    this.endpoint = endpoint;
    this.tbl = $(tbl_id);
    this.footnotes = new TableFootnotes();
    this.build_table();
    this.endpoint.addObserver(this);
};
EndpointTable.prototype = {
    update: function(status){
        this.build_table();
    },
    build_table: function(){
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
    },
    hasValues: function(val){
        return _.chain(this.endpoint.data.groups)
                .map(function(d){return d[val];})
                .any($.isNumeric)
                .value();
    },
    build_header: function(){
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

        this.hasN = this.hasValues("n");
        if(this.hasN) tr.append('<th>Number of Animals</th>');

        switch (d.data_type){
            case "D":
            case "DC":
                tr.append('<th>Incidence</th>')
                  .append('<th>Percent Incidence</th>');
                break;
            case "P":
                tr.append('<th>Response ({0}% CI)</th>'.printf(d.confidence_interval*100));
                break;
            case "C":
                txt = "Response"
                if (this.endpoint.data.response_units){
                    txt += " ({0})".printf(this.endpoint.data.response_units);
                }
                tr.append($("<th>").text(txt));
                this.hasVariance = this.hasValues("variance");
                if(this.hasVariance) tr.append('<th>{0}</th>'.printf(d.variance_name));
                break;
            default:
                throw("Unknown data type.");
        }

        this.number_columns = tr.children().length;
        this.thead = $('<thead>').append(tr);
    },
    build_body: function(){
        this.tbody = $('<tbody></tbody>');
        var self = this;
        this.endpoint.data.groups.forEach(function(v, i){

            if (!v.isReported) return;

            var tr = $('<tr>'),
                dose = v.dose.toHawcString();

            dose = dose + self.endpoint.add_endpoint_group_footnotes(self.footnotes, i);

            tr.append('<td>{0}</td>'.printf(dose));

            if(self.hasN) tr.append('<td>{0}</td>'.printf(v.n || "NR"));

            if (self.endpoint.data.data_type == 'C') {
                tr.append('<td>{0}</td>'.printf(v.response));
                if(self.hasVariance) tr.append('<td>{0}</td>'.printf(v.variance || "NR"));
            } else if (self.endpoint.data.data_type == 'P') {
                tr.append("<td>{0}</td>".printf(self.endpoint.get_pd_string(v)));
            } else {
                tr.append('<td>{0}</td>'.printf(v.incidence))
                  .append('<td>{0}%</td>'.printf(self.endpoint._dichotomous_percent_change_incidence(v)));
            }
            self.tbody.append(tr);
        });
    },
    build_footer: function(){
        var txt = this.footnotes.html_list().join('<br>');
        this.tfoot = $('<tfoot><tr><td colspan="{0}">{1}</td></tr></tfoot>'.printf(this.number_columns, txt));
    },
    build_colgroup: function(){
        this.colgroup = $('<colgroup></colgroup>');
        var self = this;
        for(var i=0; i<this.number_columns; i++){
            self.colgroup.append('<col style="width:{0}%;">'.printf((100/self.number_columns)));
        }
    }
};


var EndpointListTable = function(endpoints, dose_id){
    if(dose_id) _.each(endpoints, function(e){e.switch_dose_units(dose_id);});
    this.endpoints = endpoints;
    this.tbl = new BaseTable();
};
EndpointListTable.prototype = {
    build_table: function(){

        if(this.endpoints.length === 0)
            return '<p>No endpoints available.</p>';

        var tbl = this.tbl,
            headers = [
                'Study',
                'Experiment',
                'Animal Group',
                'Endpoint',
                'Units',
                'NOEL',
                'LOEL',
            ];
        tbl.setColGroup([12, 16, 17, 31, 10, 7, 7]);
        tbl.addHeaderRow(headers);
        this.endpoints.forEach(function(v){
            tbl.addRow(v.build_endpoint_list_row());
        });
        return tbl.getTbl();
    },
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
    this.endpoint.renderPlot($('#' + plot_div_id));

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
_.extend(DRPlot.prototype, D3Plot.prototype, {
    update: function(status){
        if (status.status === "dose_changed") this.dose_scale_change();
    },
    dose_scale_change: function(){
        // get latest data from endpoint
        this.remove_bmd_lines();
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
    },
    build_plot: function() {
        try{
            delete this.error_bars_vertical;
            delete this.error_bars_upper;
            delete this.error_bars_lower;
            delete this.error_bar_group;
        }catch (err){}
        this.plot_div.html('');
        this.get_plot_sizes();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.add_dr_error_bars();
        this.add_dose_response();
        this.add_selected_endpoint_BMD();
        this.render_bmd_lines();
        this.build_x_label();
        this.build_y_label();
        this.add_title();
        this.add_legend();
        this.customize_menu();

        var plot = this;
        this.y_axis_label.on("click", function(v){plot.toggle_y_axis();});
        this.x_axis_label.on("click", function(v){plot.toggle_x_axis();});
        this.trigger_resize();
    },
    customize_menu: function(){
        if (this.menu_div){
            this.menu_div.remove();
            delete this.menu_div;
        }
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
       if (this.endpoint.doses.length>1){
           options = {id: 'toggle_dose_units',
                      cls: 'btn btn-mini',
                      title: 'Change dose-units representation',
                      text: '',
                      icon: 'icon-certificate',
                      on_click: function(){plot.endpoint.toggle_dose_units();}};
           plot.add_menu_button(options);
       }
    },
    toggle_y_axis: function(){
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
    },
    toggle_x_axis: function(){
        // get minimum non-zero dose and then set all control doses
        // equal to ten-times lower than the lowest dose
        if(window.event && window.event.stopPropagation) event.stopPropagation();
        var egs = this.endpoint.data.groups;
        if (this.x_axis_settings.scale_type == 'linear'){
            this.x_axis_settings.scale_type = 'log';
            this.x_axis_settings.number_ticks = 1;
            this.x_axis_settings.label_format = d3.format(",.f");
        } else {
            this.x_axis_settings.scale_type = 'linear';
            this.x_axis_settings.number_ticks = 5;
            this.x_axis_settings.label_format = undefined;
        }
        this._setPlottableDoseValues();
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.x_axis_change_chart_update();
    },
    _setPlottableDoseValues: function(){
        var egs = this.endpoint.data.groups;
        if (this.x_axis_settings.scale_type == 'linear'){
            this.min_x = d3.min(_.pluck(this.values, 'x'));
            this.x_axis_settings.domain = [this.min_x-this.max_x*this.buff, this.max_x*(1+this.buff)];
        } else {
            this.min_x = d3.min(_.pluck(this.values, 'x_log'));
            this.x_axis_settings.domain = [this.min_x/10, this.max_x*(1+this.buff)];
        }
    },
    set_defaults: function(){
        // Default settings for a DR plot instance
        this.line_colors = ['#BF3F34', '#545FF2', '#D9B343', '#228C5E', '#B27373']; //bmd lines
        this.padding = {top:40, right:20, bottom:40, left:60};
        this.buff = 0.05; // addition numerical-spacing around dose/response units
        this.radius = 7;
        this.x_axis_settings = {
            'scale_type': this.endpoint.defaultDoseAxis(),
            'text_orient': "bottom",
            'axis_class': 'axis x_axis',
            'gridlines': true,
            'gridline_class': 'primary_gridlines x_gridlines',
            'number_ticks': 5,
            'axis_labels':true,
            'label_format':undefined //default
        };

        this.y_axis_settings = {
            'scale_type': 'linear',
            'text_orient': "left",
            'axis_class': 'axis y_axis',
            'gridlines': true,
            'gridline_class': 'primary_gridlines y_gridlines',
            'number_ticks': 6,
            'axis_labels':true,
            'label_format':undefined //default
        };
    },
    get_plot_sizes: function(){
        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
        this.h = this.w; //plot height
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
    },
    y_axis_change_chart_update: function(){
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
        this.render_bmd_lines();
    },
    x_axis_change_chart_update: function(){
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
        this.render_bmd_lines();
    },
    get_dataset_info: function(){
        // Get values to be used in dose-response plots
        var ep = this.endpoint.data,
            self = this,
            values, sigs_data,
            dose_units = this.endpoint.dose_units;

        values = _.chain(ep.groups)
         .map(function(v, i){
            var y,
                cls = 'dose_points',
                txts = [
                    "Dose = {0} {1}".printf(v.dose, dose_units),
                    "N = {0}".printf(v.n)
                ];

            if (ep.data_type =='C'){
                y = v.response;
                txts.push(
                    "Response = {0} {1}".printf(v.response, ep.response_units),
                    "{0} = {1}".printf(ep.variance_name, v.variance)
                );
            } else if (ep.data_type =='P'){
                y = v.response;
                txts.push("Response = {0}".printf(self.endpoint.get_pd_string(v)));
            } else {
                y = v.incidence/v.n;
                txts.push("Incidence = {0} {1}".printf(v.incidence, ep.response_units));
            }

            if (ep.LOEL == i) cls += ' LOEL';
            if (ep.NOEL == i) cls += ' NOEL';

            return {
                x:          v.dose,
                x_log:      v.dose,
                y:          y,
                cls:        cls,
                isReported: v.isReported,
                y_lower:    v.lower_ci,
                y_upper:    v.upper_ci,
                txt:        txts.join('\n'),
                significance_level: v.significance_level
            }
        })
        .filter(function(d){return d.isReported;})
        .value();

        if(values.length>2) values[0].x_log = values[1].x_log/10;

        sigs_data = _.chain(values)
            .filter(function(d){return d.significance_level>0;})
            .map(function(v){
                return {
                    'x': v.x,
                    'significance_level': v.significance_level,
                    'y': v.y_upper || v.y
                }
            })
            .value();

        _.extend(this, {
            title_str:      this.endpoint.data.name,
            x_label_text:   "Dose ({0})".printf(this.endpoint.dose_units),
            y_label_text:   "Response ({0})".printf(this.endpoint.data.response_units),
            values:         values,
            sigs_data:      sigs_data,
            max_x:          d3.max(ep.groups, function(datum) { return datum.dose; }),
        });

        this._setPlottableDoseValues();

        if (ep.groups.length>0){
            var max_upper = d3.max(values, function(d){return d.y_upper || d.y;}),
                max_sig = d3.max(sigs_data, function(d){return d.y;});

            this.min_y = d3.min(values, function(d){return d.y_lower || d.y;});
            this.max_y = d3.max([max_upper, max_sig]);
        }
    },
    add_axes: function(){
        // customizations for axis updates
        $.extend(this.x_axis_settings, {
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
    },
    add_selected_endpoint_BMD: function(){
        // Update BMD lines based on dose-changes
        var self = this;
        if ((this.endpoint.data.BMD) &&
            (this.endpoint.data.BMD.dose_units_id == this.endpoint.dose_units_id)){
            var append = true;
            self.bmd.forEach(function(v, i){
                if (v.BMD.id === self.endpoint.data.BMD.id){append = false;}
            });
            if (append){this.add_bmd_line(this.endpoint.data.BMD, 'd3_bmd_selected');}
        }
    },
    add_dr_error_bars: function(update){
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

        var bars = this.values.filter(function(v){
            return ($.isNumeric(v.y_lower)) && ($.isNumeric(v.y_upper));
            }),
            bar_options  = {
                data: bars,
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
    },
    add_dose_response: function(update) {

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
    },
    clear_legend: function(){
        //remove existing legend
        $($(this.legend)[0]).remove();
        $(this.plot_div.find('.legend_circle')).remove();
        $(this.plot_div.find('.legend_text')).remove();
    },
    add_legend: function(){
        // clear any existing legends
        this.clear_legend();

        var legend_settings = {};
        legend_settings.items = [{'text':'Doses in Study', 'classes':'dose_points', 'color':undefined}];
        if (this.plot_div.find('.LOEL').length > 0) { legend_settings.items.push({'text': 'LOEL', 'classes': 'dose_points LOEL', 'color': undefined}); }
        if (this.plot_div.find('.NOEL').length > 0) { legend_settings.items.push({'text': 'NOEL', 'classes': 'dose_points NOEL', 'color': undefined}); }
        var doseUnits = parseInt(this.endpoint.dose_units_id);
        this.bmd
            .filter(function(d){
                return d.dose_units_id === doseUnits;
            })
            .forEach(function(d){
                legend_settings.items.push({
                    'text': d.name,
                    'classes': '',
                    'color': d.stroke,
                });
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
    },
    cleanup_before_change: function(){
        this.remove_bmd_lines();
    },
    add_bmd_line: function(line){
        this.bmd.push(line);
        this.render_bmd_lines();
    },
    remove_bmd_line: function(model_id){
        this.bmd = _.reject(this.bmd, function(d){
            return d.id === model_id;
        });
        this.render_bmd_lines();
    },
    render_bmd_lines: function(){
        this.remove_bmd_lines();

        var doseUnits = parseInt(this.endpoint.dose_units_id),
            lines = this.bmd.filter(function(d){
                return d.dose_units_id === doseUnits;
            }),
            x = this.x_scale,
            xs = this.x_scale.ticks(100),
            y = this.y_scale,
            liner = d3.svg.line()
                .x(function(d){return x(d.x);})
                .y(function(d){return y(d.y);})
                .interpolate('linear');

        var bmds = _.chain(lines)
                    .filter(function(d){
                        return d.bmd_line !== undefined;
                    })
                    .map(function(d){
                        return [
                            {
                                x1: x(d.bmd_line.x),
                                x2: x(d.bmd_line.x),
                                y1: y.range()[0],
                                y2: y(d.bmd_line.y),
                                stroke: d.stroke,
                            },
                            {
                                x1: x.range()[0],
                                x2: x(d.bmd_line.x),
                                y1: y(d.bmd_line.y),
                                y2: y(d.bmd_line.y),
                                stroke: d.stroke,
                            },
                        ];
                    })
                    .flatten()
                    .value();

        var bmdls = _.chain(lines)
                    .filter(function(d){
                        return d.bmdl_line !== undefined;
                    })
                    .map(function(d){
                        return [
                            {
                                x1: x(d.bmdl_line.x),
                                x2: x(d.bmdl_line.x),
                                y1: y.range()[0],
                                y2: y(d.bmdl_line.y),
                                stroke: d.stroke,
                            },
                            {
                                x1: x.range()[0],
                                x2: x(d.bmdl_line.x),
                                y1: y(d.bmdl_line.y),
                                y2: y(d.bmdl_line.y),
                                stroke: d.stroke,
                            },
                        ];
                    })
                    .flatten()
                    .value();

        var g = this.vis
            .append('g')
            .attr('class', 'bmd');

        // add lines
        g.selectAll('path')
            .data(lines)
            .enter()
                .append('path')
                .attr('class', 'bmd_line')
                .attr('d', function(d){ return liner(d.getData(xs)); })
                .attr('stroke', function(d){ return d.stroke; });

        // add bmd lines
        g.selectAll('line.bmd')
            .data(bmds)
            .enter()
                .append('line')
                .attr('class', 'bmd_line')
                .attr('x1', function(d){return d.x1; })
                .attr('x2', function(d){return d.x2; })
                .attr('y1', function(d){return d.y1; })
                .attr('y2', function(d){return d.y2; })
                .attr('stroke', function(d){return d.stroke; });

        // add bmdl lines
        g.selectAll('line.bmd')
            .data(bmdls)
            .enter()
                .append('line')
                .attr('class', 'bmd_line')
                .attr('x1', function(d){return d.x1; })
                .attr('x2', function(d){return d.x2; })
                .attr('y1', function(d){return d.y1; })
                .attr('y2', function(d){return d.y2; })
                .attr('stroke', function(d){return d.stroke; });

        this.add_legend();
    },
    remove_bmd_lines: function(){
        this.vis
            .selectAll('g.bmd')
            .remove();
    },
});


var Barplot = function(endpoint, plot_id, options, parent){
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
_.extend(Barplot.prototype, D3Plot.prototype, {
    build_plot: function(){
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
    },
    customize_menu: function(){
        if (this.menu_div){
            this.menu_div.remove();
            delete this.menu_div;
        }
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

       if (this.endpoint.doses.length>1){
           options = {id: 'toggle_dose_units',
                      cls: 'btn btn-mini',
                      title: 'Change dose-units representation',
                      text: '',
                      icon: 'icon-certificate',
                      on_click: function(){plot.endpoint.toggle_dose_units();}};
           plot.add_menu_button(options);
       }
    },
    toggle_y_axis: function(){
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
    },
    update: function(status){
        if (status.status === "dose_changed"){
            this.dose_scale_change();
        }
    },
    dose_scale_change: function(){
        this.get_dataset_info();
        if (this.parent && this.parent.plot === this){
            this.x_axis_settings.domain = _.pluck(this.values, "dose");
            this.x_scale = this._build_scale(this.x_axis_settings);
            this.x_axis_change_chart_update();
            this.build_x_label();
        }
    },
    set_defaults: function(){
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
    },
    get_plot_sizes: function(){
        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
        this.h = this.w; //plot height
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
    },
    get_dataset_info: function(){

        this.get_plot_sizes();
        // space lines in half-increments
        var values, val, txt, cls, sigs_data,
            default_y_scale = this.default_y_scale,
            e = this.endpoint,
            data_type = e.data.data_type,
            min = Infinity,
            max = -Infinity;

        values = _.chain(this.endpoint.data.groups)
            .map(function(v, i){

                if(data_type=='C'){
                    val = v.response;
                    txt = v.response;
                } else if (data_type =='P'){
                    val = v.response;
                    txt = e.get_pd_string(v);
                } else{
                    val = v.incidence/v.n;
                    txt = val;
                }

                cls = 'dose_bars'
                if(e.data.NOEL == i) cls += ' NOEL';
                if(e.data.LOEL == i) cls += ' LOEL';

                min = Math.min(min, v.lower_ci || val);
                max = Math.max(max, v.upper_ci || val);

                return {
                    isReported: v.isReported,
                    dose:       v.dose,
                    value:      val,
                    high:       v.upper_ci,
                    low:        v.lower_ci,
                    txt:        txt,
                    classes:    cls,
                    significance_level:     v.significance_level,
                }
            })
            .filter(function(d){return d.isReported;})
            .value();

        sigs_data = _.chain(values)
            .filter(function(v){return v.significance_level>0;})
            .map(function(v){
                return {
                    x: v.dose,
                    y: v.high || v.value,
                    significance_level: v.significance_level,
                }
            }).value();

        if(this.endpoint.data.data_type=='C'){
            min = min - (max*this.buff);
        } else {
            min = 0;
        }
        max = max*(1+this.buff);
        if (this.default_y_scale == "log"){
            min = Math.pow(10, Math.floor(Math.log10(min)));
            max = Math.pow(10, Math.ceil(Math.log10(max)));
        }

        _.extend(this, {
            title_str: this.endpoint.data.name,
            x_label_text: "Doses ({0})".printf(this.endpoint.dose_units),
            y_label_text: "Response ({0})".printf(this.endpoint.data.response_units),
            values: values,
            sigs_data: sigs_data,
            min_y: min,
            max_y: max
        });
    },
    add_axes: function() {
        $.extend(this.x_axis_settings, {
            domain: _.pluck(this.values, "dose"),
            number_ticks: this.values.length,
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
    },
    add_bars: function(){
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
    },
    x_axis_change_chart_update: function(){
        this.xAxis.scale(this.x_scale);
        this.vis.selectAll('.x_axis')
            .transition()
            .call(this.xAxis);
    },
    y_axis_change_chart_update: function(){
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
    },
    add_error_bars: function(){
        var hline_width = this.w * 0.02,
            x = this.x_scale,
            y = this.y_scale,
            bars = this.values.filter(function(v){
                return ($.isNumeric(v.low)) && ($.isNumeric(v.high));
            });

        this.error_bar_group = this.vis.append("g")
                .attr('class','error_bars');

        bar_options = {
            data: bars,
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
    },
    add_legend: function(){
        var legend_settings = {};
        legend_settings.items = [{'text':'Doses in Study', 'classes':'dose_points', 'color':undefined}];
        if (this.plot_div.find('.LOEL').length > 0) { legend_settings.items.push({'text':'LOEL', 'classes':'dose_points LOEL', 'color':undefined}); }
        if (this.plot_div.find('.NOEL').length > 0) { legend_settings.items.push({'text':'NOEL', 'classes':'dose_points NOEL', 'color':undefined}); }
        if (this.plot_div.find('.BMDL').length > 0) { legend_settings.items.push({'text':'BMDL', 'classes':'dose_points BMDL', 'color':undefined}); }
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
    },
    cleanup_before_change: function(){
    }
});
