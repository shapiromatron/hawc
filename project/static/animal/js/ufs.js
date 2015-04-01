var UncertaintyFactor = function(parsed_json, endpoint, changed){
    this.uf_type = parsed_json.uf_type;
    this.label_text_short = 'UF<sub>' + this.uf_type[2] + '</sub>';
    this.label_text_long = UncertaintyFactor.labels[this.uf_type] +  ' (' + this.label_text_short + ')';
    this.description = parsed_json.description;
    this.value = parsed_json.value;
    this.changed = changed;
    this.endpoint = endpoint;
    this.pk = parsed_json.pk;
    this.url = parsed_json.url;
};
_.extend(UncertaintyFactor, {
    ufs: [
       {uf_type: 'UFA', description:'', label: 'Interspecies uncertainty', value:10},
       {uf_type: 'UFH', description:'', label: 'Interspecies variability', value:10},
       {uf_type: 'UFS', description:'', label: 'Subchronic to chronic extrapolation', value:1},
       {uf_type: 'UFL', description:'', label: 'Use of a LOAEL in absence of a NOAEL', value:1},
       {uf_type: 'UFD', description:'', label: 'Database incomplete', value:3},
       {uf_type: 'UFO', description:'', label: 'Other', value:1}
    ],
    labels: {
        'UFA': 'Interspecies uncertainty',
        'UFH': 'Interspecies variability',
        'UFS': 'Subchronic to chronic extrapolation',
        'UFL': 'Use of a LOAEL in absence of a NOAEL',
        'UFD': 'Database incomplete',
        'UFO': 'Other'
    }
});
UncertaintyFactor.prototype = {
    build_submission_object: function(endpoint_pk){
        var obj = {uf_type: this.uf_type,
                   description: this.description,
                   value: this.value,
                   endpoint: endpoint_pk};
        if(this.pk){obj.pk = this.pk;}
        return obj;
    },
    build_form: function(){
        var lbl = $('<label>' + this.label_text_short +' </label>'),
            self = this,
            input = $('<input data-name="' + this.uf_type + '" type="text" value="' + this.value +'" class="input-mini">')
                .on('change', function(){
                    var d = $(this).data();
                    d.val = $(this).val();
                    d.val = parseFloat(d.val);
                    if (isNaN(d.val) || !isFinite(d.val) || d.val<=0){
                        $(this).val(1);
                        d.val = 1;
                    }
                    self.endpoint.uf_changed(d);
                })
                .on('click', function(){
                    self.endpoint.description_div.set_UF(self);
                });
        lbl.append(input);
        this.input_field = input;
        return lbl;
    },
    change: function(obj){
        this.changed=true;
        this.value = obj.val;
        this.input_field.val(obj.val);
    },
    build_popover: function(){
        return  $('<a href="' + this.url + '" class="popovers">' + this.value + '</a>')
                    .attr({'data-placement': 'bottom',
                           'data-trigger': 'hover',
                           'data-toggle':'popover',
                           'data-content': this.description,
                           'data-original-title': UncertaintyFactor.labels[this.uf_type]});
    },
    set_description: function(txt){
        if (txt !== this.description){
            this.description = txt;
            this.changed = true;
            this.endpoint.notifyObservers();
        }
    },
    build_table_row: function(){

        return $('<tr></tr>').append('<td>{0}</td>'.printf(this.label_text_long))
                             .append('<td>{0}</td>'.printf(this.value))
                             .append('<td>{0}</td>'.printf(this.description));
    }
};


var UFDescription = function(){
    var self = this;
    this.div = $('<div style="display:none"></div>');
    this.label = $('<label>Description</label>');
    this.input = $('<textarea class="span12">');
    this.div.append([this.label, this.input]);
    this.input.on('blur', function(){self.hide();});
};
UFDescription.prototype = {
    hide: function(){
        this.div.fadeOut('fast');
        this.uf.set_description(this.input.val());
        this.uf = undefined;
    },
    set_UF: function(uf){
        this.uf = uf;
        this.label.html(uf.label_text_long + ' factor justification:');
        this.input.val(uf.description);
        this.div.fadeIn('fast');
    }
};


var UFsContainer =  function(endpoints, name, options){
    Aggregation.call(this, endpoints, name); // call parent constructor
    this.options = options;
    this.x_domain = [Infinity, -Infinity];
    var self = this;
    this.endpoints.forEach(function(v,i){
        v.addObserver(self);
        v.set_UF_container(self);
    });
    this.plot_div = $(options.id_plot);
    if (this.options.edit_mode) { this.individual_ufs = $(options.id_individual_ufs);}
    this.update_domain();
    this.build_all_plots();
     if (this.options.edit_mode) {this.build_change_all_fields();}

    if (this.options.id_uf_table){
        this.uf_table = new UFsContainerTable(this, options.id_uf_table);
    }
};
UFsContainer.prototype = {
    update_domain: function(){
        //update global domain as needed
        var domain_changed = false,
            x_domain = [d3.min(this.endpoints.map(function(v,i){return v.rfd;})),
                        d3.max(this.endpoints.map(function(v,i){return v.pod.value;}))];
        if (x_domain[0] != this.x_domain[0]){domain_changed = true;}
        if (x_domain[1] != this.x_domain[1]){domain_changed = true;}
        this.x_domain = x_domain;
        this.domain_changed = domain_changed;
    },
    get_global_domain: function(){
        return {domain: this.x_domain, changed: this.domain_changed};
    },
    update: function(){
        this.update_domain();
        this.redraw_all_plots();
    },
    build_all_plots: function(){

        if(this.options.edit_mode){
            // build individual endpoint plots
            this.endpoints.forEach(function(v,i){
                v.build_uf_plot();
            });
        }

        // build master-plot
        var options = {build_plot_startup: true,
                       default_x_axis: 'log',
                       show_legend: true,
                       show_title: true,
                       title: this.name,
                       show_y_labels: true,
                       padding: {top:30, right:70, bottom:40, left:10},
                       show_menu_bar: true};
        this.uf_plot = new UncertaintyFactorPlot(this.endpoints, this.plot_div, options);
    },
    redraw_all_plots: function(first_time){
        //redraw main plot and all additional plots
        if (this.domain_changed){
            this.endpoints.forEach(function(v,i){
                v.uf_plot.update_plot();
            });
            this.uf_plot.update_plot();
        }
    },
    submit_data: function(){
        // submit data to save to database
        ufs = [];
        this.endpoints.forEach(function(v,i){
            ufs=ufs.concat(v.build_submission_object());
        });
        return JSON.stringify({ufs: ufs});
    },
    update_all_ufs: function(opt){
        // update all endpoints, whenever the global uncertainty value fields are used.
        this.endpoints.forEach(function(v, i){
            v.uf_changed(opt);
        });
    },
    build_change_all_fields: function(){
        // associate the global UF input fields
        var self = this;
        $.each($(this.options.id_global_fields  + ' input'), function(i, v){
            $(v).on('change', function(v, i){
                var d = $(this).data();
                d.val = parseFloat($(this).val());
                if (isNaN(d.val)){$(this).val("-"); return false;}
                if(!isFinite(d.val) || d.val<=0){
                    $(this).val(1);
                    d.val = 1;
                }
                self.update_all_ufs(d);
            });
        });
    }
};
_.extend(UFsContainer.prototype, Aggregation.prototype);


var UFsContainerTable = function(ufs_container, table_id){
    this.ufs_container = ufs_container;
    this.table = $(table_id);
    this.build_table();
};
UFsContainerTable.prototype = {
    build_header_row: function(){
        var tr = $('<tr></tr>');
        tr.append('<th>Study</th>')
          .append('<th>Experiment</th>')
          .append('<th>Animal Group</th>')
          .append('<th>Endpoint</th>');
        UncertaintyFactor.ufs.forEach(function(v,i){
            tr.append('<th>UF<sub>' + v.uf_type[2] + '</sub></th>');
        });
        return tr;
    },
    build_table: function(){
        var thead = this.table.find('thead').html('');
        var tbody = this.table.find('tbody').html('');
        thead.append(this.build_header_row());
        this.ufs_container.endpoints.forEach(function(v,i){
            tbody.append(v.build_table_row());
        });
    }
};


var ReferenceValue = function(dataset, options){
    Observee.apply(this, arguments);
    this.data = dataset;
    this.unpack_endpoint_ufs();
    this.calculate_plot_values();
    this.set_domain_calcs();
};
_.extend(ReferenceValue.prototype, Observee.prototype, {
    unpack_endpoint_ufs: function(){
        UFEndpoint.prototype.unpack_endpoint_ufs.apply(this);
    },
    create_plot_dataset: function(){

        var plot_data = {pk: this.data.pk,
                         pod: this.data.point_of_departure,
                         rfd: this.data.rfd,
                         name: this.data.name,
                         dose_units: this.data.units};
        this.data.ufs.forEach(function(v,i){
                    plot_data[v.uf_type] = {plot_value: v.plot_value,
                                    value: v.value,
                                    name: v.uf_type,
                                    label: v.label_text_long,
                                    description: v.description};
        });
        return plot_data;
    },
    calculate_plot_values: function(){
        var threes = 0, last_v;
        this.data.ufs.forEach(function(v, i){
            if (v.value === 3){
                threes += 1;
                if (threes % 2 === 0){
                    last_v.plot_value = Math.sqrt(10);
                    v.plot_value = Math.sqrt(10);
                    last_v = undefined;
                } else {
                    v.plot_value = v.value;
                    last_v = v;
                }
            } else {
                v.plot_value = v.value;
            }
        });
    },
    set_domain_calcs: function(){
        var self = this;
        this.ufs_container = {get_global_domain: function(){
             return {domain: [self.data.rfd, self.data.point_of_departure], changed: false}; }};
    },
    build_uf_table: function(div){
        var tbl = $('<table class="table table-condensed table-striped"></table>'),
            colgroup = $('<colgroup><col style="width:25%"><col style="width:10%"><col style="width:65%"></col></colgroup>'),
            thead = $('<thead><th>Uncertainty Factor</th><th>Value</th><th>Description</th></thead>'),
            tbody = $('<tbody></tbody>callback');

        // sort table by uncertainty factor, decreasing order
        var sorted = this.data.ufs.sort(function(a,b){
                return (a.value > b.value)?-1:((b.value > a.value)?1:0);
            });

        this.data.ufs.forEach(function(v){
            tbody.append(v.build_table_row());
        });
        $(div).html(tbl.html([colgroup, thead, tbody]));
    }
});


var UFEndpoint = function(endpoint, options){
    Endpoint.call(this, endpoint); // call parent constructor
    this.uf_form_div = $(options.uf_form_div);
    this.unpack_endpoint_ufs();
    this.pod = this.get_pod();
    this.calculate_rfd();
    this.create_uf_form();
};
UFEndpoint.prototype = {
    unpack_endpoint_ufs: function(){
        // unpack existing UFs if found, or if not, create default new ones. This
        // removes the current array from the endpoint and re-inserts a new
        // UncertaintyFactor object back into the array
        var self = this,
            current_ufs = this.data.ufs;
        this.data.ufs = [];
        UncertaintyFactor.ufs.forEach(function(v,i){
            var match_found=false;
            current_ufs.forEach(function(v2, i2){
                if (v.uf_type === v2.uf_type){
                    self.data.ufs.push(new UncertaintyFactor(v2, self, false));
                    match_found=true;
                }
            });
            if (!match_found) {
                self.data.ufs.push(new UncertaintyFactor(v, self, true));
            }
        });
    },
    build_uf_plot: function(){
        var options = {build_plot_startup: true,
                       default_x_axis: 'log',
                       show_legend: false,
                       show_title: false,
                       show_y_labels: false,
                       padding: {top:20, right:20, bottom:40, left:20},
                       show_menu_bar: false};
        this.uf_plot = new UncertaintyFactorPlot([this], this.plot_div, options);
    },
    create_uf_form: function(){
        this.container = $('<div></div>').attr('class', 'row-fluid');
        this.inp_form = $('<form></form>').attr('class','form-inline');
        this.inp_fieldset = $('<fieldset></fieldset>');
        var a = $('<a href="' + this.data.url + '">' + this.data.name + '</a>');
        this.inp_fieldset.append($('<legend></legend>').append(a));
        var inputs = $('<div></div>').attr('class', 'span5');
        this.plot_div = $('<div></div>').attr('class', 'span6 d3_container');
        this.pod_text = $('<p></p>');
        this.rfd_text = $('<p></p>');
        var text_div = $('<div></div>').append(this.pod_text, this.rfd_text);
        inputs.append(text_div);
        self = this;
        this.data.ufs.forEach(function(v,i){
            inputs.append(v.build_form());
        });
        this.inp_fieldset.append([inputs, this.plot_div]);
        this.inp_form.append(this.inp_fieldset);
        this.description_div = new UFDescription({single_uf: true});
        this.inp_form.append(this.description_div.div);
        this.container.append(this.inp_form);
        this.print_pod_rfd();
        this.uf_form_div.append(this.container);
    },
    set_UF_container: function(container){
        this.ufs_container = container;
    },
    print_pod_rfd: function(){
        var f = d3.format("0.5g");
        if (this.pod_text){
            this.pod_text.html('POD: ' + f(this.pod.value) + ' ' + this.data.dose_units + ' (' + this.pod.type + ')');
            this.rfd_text.html('RfD: ' + f(this.rfd) + ' ' + this.data.dose_units);
        }
    },
    create_plot_dataset: function(){
        var plot_data = {pk: this.data.id,
                         pod: this.pod.value,
                         rfd: this.rfd,
                         name: this.data.animal_group.experiment.study.short_citation + "- " +
                               this.data.animal_group.name + ": " + this.data.name,
                         dose_units: this.data.dose_units};
        this.data.ufs.forEach(function(v,i){
                    plot_data[v.uf_type] = {plot_value: v.plot_value,
                                    value: v.value,
                                    name: v.uf_type,
                                    label: v.label_text_long,
                                    description: v.description};
        });
        return plot_data;
    },
    calculate_rfd: function(){
        // in RfD math, 3*3=10. Therefore, we create two separate sets of values,
        // one for the values written by users ('value'), and the other for
        // representation in the math and plots for rfd calculation ('plot_value')
        var pod = this.pod.value;
        var threes = 0, last_v;
        this.data.ufs.forEach(function(v, i){
            if (v.value === 3){
                threes += 1;
                if (threes % 2 === 0){
                    last_v.plot_value = Math.sqrt(10);
                    v.plot_value = Math.sqrt(10);
                    pod = pod * 3 / 10;
                    last_v = undefined;
                } else {
                    v.plot_value = v.value;
                    last_v = v;
                    pod = pod / v.plot_value;
                }
            } else {
                v.plot_value = v.value;
                pod = pod / v.plot_value;
            }
        });
        this.rfd = pod;
        this.print_pod_rfd();
        this.notifyObservers();
    },
    build_table_row: function(){
        var tr = $('<tr></tr>');
        tr.append($('<td></td>').html('<a href="{0}">{1}</a>'
                  .printf(this.data.animal_group.experiment.study.study_url, this.data.animal_group.experiment.study.short_citation)));
        tr.append($('<td></td>').html('<a href="{0}">{1}</a>'
                  .printf(this.data.animal_group.experiment.url, this.data.animal_group.experiment.name)));
        tr.append($('<td></td>').html('<a href="{0}">{1}</a>'
                  .printf(this.data.animal_group.url, this.data.animal_group.name)));
        tr.append($('<td></td>').html('<a href="{0}">{1}</a>'
                  .printf(this.data.url, this.data.name)));
        this.data.ufs.forEach(function(v, i){
            var td = $('<td></td>').append(v.build_popover());
            tr.append(td);
        });
        return tr;
    },
    uf_changed: function(obj){
        // update the uncertainty factor that changed
        this.data.ufs.forEach(function(v,i){
            if (obj.name === v.uf_type){v.change(obj);}
        });
        this.calculate_rfd();
    },
    build_submission_object: function(){
        // prepare data for submission object
        var ufs = [], endpoint_pk = this.data.pk;
        this.data.ufs.forEach(function(v,i){
            // only send stuff that's changed
            if (v.changed){ufs.push(v.build_submission_object(endpoint_pk));}
        });
        return ufs;
    }
};
_.extend(UFEndpoint.prototype, Endpoint.prototype);


var UncertaintyFactorPlot = function(objects, plot_div, options){
    // Exposure-Response Horizontal plot
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.options = options;
    this.options.padding.left_original = this.options.padding.left;
    this.set_defaults();
    this.y_axis_settings.gridlines = this.options.show_y_labels;
    this.y_axis_settings.axis_labels = this.options.show_y_labels;
    this.padding = this.options.padding; // t, r, b, l (clockwise)
    this.plot_div = plot_div;
    this.objects = objects; // expected array
    this.objects.forEach(function(v,i){v.addObserver(self);}); //observe all
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(UncertaintyFactorPlot.prototype, D3Plot.prototype, {
    update: function(){
        this.update_plot();
    },
    update_plot: function(){
        var new_domain = this.objects[0].ufs_container.get_global_domain();
        this.x_axis_settings.domain = new_domain.domain;
        this.get_dataset();
        this.x_axis_change_chart_update(new_domain.changed);
    },
    build_plot: function(){
        this.plot_div.html('');
        this.get_plot_sizes();
        this.get_dataset();
        this.build_plot_skeleton(true);
        this.x_axis_settings.domain = this.objects[0].ufs_container.get_global_domain().domain;
        this.add_axes();
        this.build_x_label();
        this.add_uf_rectangles();
        this.add_critical_points();
        this.build_text_labels();
        this.add_final_rectangle();
        if(this.options.show_menu_bar){this.add_menu();}
        if(this.options.show_title){this.add_title();}
        if(this.options.show_legend){this.add_legend();}
        if(this.options.show_y_labels){this.resize_plot_width();}
        this.trigger_resize();
    },
    resize_plot_width: function(){
        // attempt to resize plot based on the dimensions of the y-axis labels
        try{
            var label_width = this.vis.select('.y_axis').node().getBoundingClientRect().width;
            if (this.options.padding.left < this.options.padding.left_original + label_width){
                this.options.padding.left = this.options.padding.left_original + label_width;
                this.build_plot();
            }
        } catch(error) {}
    },
    x_axis_change_chart_update: function(domain_changed){
        // Assuming the plot has already been constructed once,
        // rebuild plot with updated x-scale.
        if(domain_changed){
            this.x_scale = this._build_scale(this.x_axis_settings);
            this.rebuild_x_axis();
            this.rebuild_x_gridlines({animate: true});
        }

        var y = this.y_scale,
            x = this.x_scale,
            halfway = y.rangeBand()/2;

        this.pods_dots
            .data(this.pods_data)
            .transition()
            .duration(1000)
            .attr("transform", function(d) {
                    return "translate(" + x(d.x)  + "," +
                            (y(d.y)+halfway) + ")"; });
        this.rfds_dots
            .data(this.rfds_data)
            .transition()
            .duration(1000)
            .attr("transform", function(d) {
                    return "translate(" + x(d.x)  + "," +
                            (y(d.y)+halfway) + ")"; });

        this.vis.selectAll('rect.uf_bar')
            .data(this.bars_data)
            .transition()
            .duration(1000)
            .attr("x", function(d) {return x(d.bottom);})
            .attr("width", function(d) {return x(d.top)- x(d.bottom); });

        this.build_text_labels();
    },
    build_text_labels: function(){
        var y = this.y_scale,
            x = this.x_scale,
            halfwidth = y.rangeBand()/2,
            formatNumber = d3.format("1.2e"),
            self = this;

        // add UF bar labels
        this.bars_label = this.bars_group.selectAll("text").remove();

        this.bars_label = this.bars_group.selectAll("svg.text")
            .data(this.bars_data)
          .enter().append("svg:text")
            .attr("x", function(d) {return x(d.bottom) + (x(d.top)- x(d.bottom))/2; })
            .attr("y", function(d) {return (y(d.y)+halfwidth+5);})
            .attr('class', function(d) {return 'uf_label hidden ' + d.classes;})
            .text(function(d) { return (d.value !== 1) ? d.value : ""; });

        this.pod_label = this.bars_group.selectAll("svg.text")
            .data(this.pods_data)
          .enter().append("svg:text")
            .attr("x", function(d) {return x(d.x)+10;})
            .attr("y", function(d) {return (y(d.y)+halfwidth+4);})
            .style('text-anchor','start')
            .attr('class', 'pod_label data_label hidden')
            .text(function(d) { return formatNumber(d.x); });

        this.rfd_labels = this.bars_group.selectAll("svg.text")
            .data(this.rfds_data)
          .enter().append("svg:text")
            .attr("x", function(d) {return x(d.x)-10;})
            .attr("y", function(d) {return (y(d.y)+halfwidth+4);})
            .attr('class', 'rfd_label data_label hidden')
            .style('text-anchor','end')
            .text(function(d) { return formatNumber(d.x); });
    },
    get_plot_sizes: function(){
        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // extra for margins
        this.h = this.objects.length*this.uf_bar_height*2; // +50% spacing either side
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom + menu_spacing) + 'px'}); // extra for toolbar
    },
    set_defaults: function(){
        this.buff = 0.05; // addition numerical-spacing around dose/response units

        var formatNumber = d3.format(",.f");
        this.x_axis_settings = {
            scale_type: this.options.default_x_axis || 'log',
            text_orient: "bottom",
            axis_class: 'axis x_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            number_ticks: 10,
            axis_labels: true,
            label_format: formatNumber
        };

        this.y_axis_settings = {
            scale_type: 'ordinal',
            text_orient: 'left',
            axis_class: 'axis y_axis',
            gridline_class: 'primary_gridlines y_gridlines',
            label_format: undefined //default
        };

        this.uf_order = ['UFA', 'UFH', 'UFS', 'UFL', 'UFD', 'UFO'];
        this.uf_bar_height = 30;
    },
    get_dataset: function(){

        var rfds_data = [],
            pods_data = [],
            bars_data = [],
            uf_order = this.uf_order,
            dataset = [];

        // todo: needs complete refactoring
        if (this.objects[0].constructor===ReferenceValue){
            this.objects.forEach(function(v,i){
                // get POD and RfD dataset bins
                pods_data.push({"y": v.data.pk,
                                "x": v.data.point_of_departure,
                                "name": v.data.name});
                rfds_data.push({"y": v.data.pk,
                                "x": v.data.rfd});

                var ufs_temp={};
                //unpack uncertainty bar
                v.data.ufs.forEach(function(uf){
                    ufs_temp[uf.uf_type] = {"name":v.data.name,
                                            "plot_value": uf.plot_value,
                                            "value": uf.value,
                                            "label": uf.label_text_long,
                                            "description": uf.description};
                });

                // get uncertainty bar size
                var top = v.data.point_of_departure;
                for(var j=0; j<uf_order.length; j++){
                    var change = top - top/ufs_temp[uf_order[j]].plot_value;
                    var bar = {"y": v.name + ' (' + v.pk + ')',
                               "classes": uf_order[j],
                               "factor": ufs_temp[uf_order[j]].plot_value,
                               "top": top,
                               "bottom": top-change,
                               "value": ufs_temp[uf_order[j]].value,
                               "label": ufs_temp[uf_order[j]].label,
                               "description": ufs_temp[uf_order[j]].description};
                    bars_data.push(bar);
                    top = top - change;
                }
            });
        } else { // it's an endpoint reference object!
            // first grab new dataset
            this.objects.forEach(function(v,i){
                if (v.data.endpoint_group.length>0) dataset.push(v.create_plot_dataset());
            });

            // now construct array for plots
            dataset.forEach(function(v, i){
                // get POD and RfD dataset bins
                pods_data.push({y: v.pk, x: v.pod, name: v.name});
                rfds_data.push({y: v.pk, x: v.rfd});

                // get uncertainty bar size
                var top = v.pod;
                for(var j=0; j<uf_order.length; j++){
                    var change = top - top/v[uf_order[j]].plot_value;
                    var bar = {"y": v.pk,
                               "classes": uf_order[j],
                               "factor": v[uf_order[j]].plot_value,
                               "top": top,
                               "bottom": top-change,
                               "value": v[uf_order[j]].value,
                               "label": v[uf_order[j]].label,
                               "description": v[uf_order[j]].description};
                    bars_data.push(bar);
                    top = top - change;
                }
            });
        }
        this.bars_data = bars_data;
        this.pods_data = pods_data;
        this.rfds_data = rfds_data;
        this.title_str = this.options.title;
        this.x_label_text = this.objects[0].dose_units;
        this.y_label_text = 'Endpoints';
    },
    add_axes: function() {
        // using plot-settings, customize axes)
        $.extend(this.x_axis_settings, {
            rangeRound: [0, this.w],
            x_translate: 0,
            y_translate: this.h
        });

        $.extend(this.y_axis_settings, {
            domain: this.pods_data.map(function(d) {return d.y;}),
            rangeRound: [0, this.h],
            number_ticks: 1,
            x_translate: 0,
            y_translate: 0
        });

        this.build_x_axis();
        this.build_y_axis();

        var pods_data = this.pods_data;
        d3.selectAll('.y_axis text')
            .text(function(v,i){
                var name;
                pods_data.forEach(function(pod){
                    if (v === pod.y) {
                        name = pod.name;
                        return;
                    }
                });
                return name;
            });
    },
    add_critical_points: function(){

        var x = this.x_scale,
            y = this.y_scale,
            halfwidth = y.rangeBand()/2,
            plot = this;

        //POD
        this.pods_dots = this.vis.selectAll("path.dot")
            .data(this.pods_data)
          .enter().append("circle")
            .attr("r","7")
            .attr("class", "pod")
            .attr("transform", function(d) {
                    return "translate(" + x(d.x) +
                            "," + (y(d.y)+halfwidth) + ")"; })
            .on('mouseover', function(){return plot.show_point_labels(plot, 'pod_label');})
            .on('mouseout', function(){return plot.hide_point_values(plot);});

        //RfD
        this.rfds_dots = this.vis.selectAll("path.dot")
            .data(this.rfds_data)
          .enter().append("circle")
            .attr("r","7")
            .attr("class", "rfd")
            .attr("transform", function(d) {
                    return "translate(" + (x(d.x)) +
                            "," + (y(d.y)+halfwidth) + ")"; })
            .on('mouseover', function(){return plot.show_point_labels(plot, 'rfd_label');})
            .on('mouseout', function(){return plot.hide_point_values(plot);});
    },
    show_point_labels: function(plot, class_name){
        bars = plot.vis.selectAll('.data_label.' + class_name)
                        .classed('hidden', false);
    },
    hide_point_values: function(plot){
        bars = plot.vis.selectAll('.data_label')
                        .classed('hidden', true);
    },
    add_uf_rectangles: function(){
        var x = this.x_scale,
            y = this.y_scale,
            uf_order = this.uf_order,
            uf_bar_height = this.uf_bar_height,
            halfway = y.rangeBand()/2,
            plot = this;

        this.bars_group = this.vis.append("g");
        this.bars = this.bars_group.selectAll("svg.ufs")
            .data(this.bars_data)
          .enter().append("rect")
            .attr("x", function(d) {return x(d.bottom); })
            .attr("y", function(d) {return (y(d.y)+halfway-uf_bar_height/2);})
            .attr("height", uf_bar_height)
            .attr("width", function(d) {return x(d.top)- x(d.bottom);})
            .attr('class', function(d) {return 'uf_bar ' + d.classes;})
            .on('mouseover', function(d){
                plot.show_rectangle_values(this, plot);
                plot.show_tooltip(d.label, d.description);
            })
            .on('mouseout', function(){
                plot.hide_rectangle_values(this, plot);
                plot.hide_tooltip();
            });
    },
    show_rectangle_values: function(bar, plot){
        bar = d3.select(bar);
        plot.bars.classed('unhovered_bar', true);
        this.uf_order.forEach(function(v, i){
            if(bar.classed(v)){
                bars = plot.vis.selectAll('rect.' + v)
                        .classed('unhovered_bar', false)
                        .classed('hovered_bar', true);
                bars = plot.vis.selectAll('.uf_label.' + v)
                        .classed('hidden', false);
            }
        });
    },
    hide_rectangle_values: function(bar, plot){
        plot.bars
            .classed('unhovered_bar', false)
            .classed('hovered_bar', false);
        plot.bars_label.classed('hidden', true);
    },
    add_legend: function(){
        var items = [],
            self = this;

        items.push({'text':'POD', 'classes':'pod', 'color':undefined});
        this.uf_order.forEach(function(v, i){
            if (self.plot_div.find('.' + v).length > 0) {items.push({text: v, classes: v, color: undefined});}
        });
        items.push({'text':'RfD', 'classes':'rfd', 'color':undefined});

        var legend_settings = {'items': items};
        legend_settings.box_padding = 5;
        legend_settings.box_t = 0;
        legend_settings.box_l = this.w+10;
        legend_settings.item_height = 20;
        legend_settings.dot_r = 5;
        this.build_legend(legend_settings);
    }
});
