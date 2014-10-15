CTPlot = function(endpoint, plot_id, options){
    //concentration x time plot
    D3Plot.call(this); // call parent constructor
    this.endpoint = endpoint;
    this.plot_div = $(plot_id);
    this.options = options || {build_plot_startup:true};
    this.set_defaults();
    this.get_dataset_info();
    if (this.options.build_plot_startup){this.build_plot();}
};

CTPlot.prototype = new D3Plot();
CTPlot.prototype.constructor = CTPlot;

CTPlot.prototype.build_plot = function(){
    this.plot_div.html('');
    this.get_plot_sizes();
    this.build_plot_skeleton(true);
    this.add_title();
    this.add_axes();
    this.add_confidence_intervals();
    this.add_lines();
    this.build_x_label();
    this.build_y_label();
    this.add_final_rectangle();
    this.add_legend();
    this.customize_menu();

    this.filter_mode=false;
    var plot = this;
    $('body').on('keydown', function() {
        if (event.ctrlKey || event.metaKey){plot.filter_y_axis();}
    });
};

CTPlot.prototype.filter_y_axis = function(){
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

CTPlot.prototype.customize_menu = function(){
    this.add_menu();
    if (this.parent){this.parent.add_toggle_button(this);}
    var plot = this;
    var options = {id:'filter_response',
                   cls: 'btn btn-mini',
                   title: 'View timepoint (shortcut: press ctrl to toggle)',
                   text: '',
                   icon: 'icon-filter',
                   on_click: function(){plot.filter_y_axis();}};
   plot.add_menu_button(options);
};

CTPlot.prototype.set_defaults = function(){
    // Default settings
    this.padding = {top:40, right:20, bottom:40, left:60};
    this.buff=0.05;

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

CTPlot.prototype.get_plot_sizes = function(){
    this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
    this.h = this.w; //plot height
    this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
};

CTPlot.prototype.add_reference_line = function(event){
    // check if in domain before continuing
    if (!this.isWithinDomain(event)){
        d3.selectAll('.selected_overlay').remove();
        return false;
    }

    var x_value = d3.mouse(event)[0],
        section = d3.bisect(this.x_scale.range(), x_value);

    if (this.last_section === section){return true;} else { this.last_section=section;}

    d3.selectAll('.selected_overlay').remove();
    this.highlighted_section = this.vis.insert("rect",".time_paths")
        .attr("x", this.x_scale(section))
        .attr("y", 0)
        .attr("width", this.x_scale.rangeBand())
        .attr("height", this.h)
        .attr('class', 'selected_overlay');

    //deep copy
    this.dummy_endpoint = $.extend(true, {}, this.endpoint);
    this.dummy_endpoint.dr = this.dummy_values[section-1];
    this.dummy_endpoint.data.dr = this.dummy_values[section-1];
    if (!this.dr_plot){
        this.dr_plot = new DRPlot(this.dummy_endpoint, '#dr_plot');
    } else {
        this.dr_plot.endpoint = this.dummy_endpoint.data;
        this.dr_plot.dr_plot_update();
    }
};

CTPlot.prototype.get_dataset_info = function(){
    // space lines in half-increments
    var y_min = Infinity, y_max = -Infinity, val, txt, cls, e,
        default_y_scale = this.default_y_scale,
        values = [], stats = [];

    this.dummy_values = [
        [{"dose": 0 ,"time": 10 ,"response": 1,"n":20,"stdev":0.5,"lower_limit":0.5,"upper_limit":1.5},
        {"dose": 25 ,"time": 10 ,"response": 12,"n":20,"stdev":6,"lower_limit":6,"upper_limit":18},
        {"dose": 50 ,"time": 10 ,"response": 25,"n":20,"stdev":12.5,"lower_limit":12.5,"upper_limit":37.5},
        {"dose": 75 ,"time": 10 ,"response": 39,"n":20,"stdev":19.5,"lower_limit":19.5,"upper_limit":58.5},
        {"dose": 100 ,"time": 10 ,"response": 51,"n":20,"stdev":25.5,"lower_limit":25.5,"upper_limit":76.5}],
        [{"dose": 0 ,"time": 20 ,"response": 2,"n":20,"stdev":1,"lower_limit":1,"upper_limit":3},
        {"dose": 25 ,"time": 20 ,"response": 17,"n":20,"stdev":8.5,"lower_limit":8.5,"upper_limit":25.5},
        {"dose": 50 ,"time": 20 ,"response": 31,"n":20,"stdev":15.5,"lower_limit":15.5,"upper_limit":46.5},
        {"dose": 75 ,"time": 20 ,"response": 49,"n":20,"stdev":24.5,"lower_limit":24.5,"upper_limit":73.5},
        {"dose": 100 ,"time": 20 ,"response": 68,"n":20,"stdev":34,"lower_limit":34,"upper_limit":102}],
        [{"dose": 0 ,"time": 30 ,"response": 3,"n":20,"stdev":1.5,"lower_limit":1.5,"upper_limit":4.5},
        {"dose": 25 ,"time": 30 ,"response": 22,"n":20,"stdev":11,"lower_limit":11,"upper_limit":33},
        {"dose": 50 ,"time": 30 ,"response": 34,"n":20,"stdev":17,"lower_limit":17,"upper_limit":51},
        {"dose": 75 ,"time": 30 ,"response": 51,"n":20,"stdev":25.5,"lower_limit":25.5,"upper_limit":76.5},
        {"dose": 100 ,"time": 30 ,"response": 67,"n":20,"stdev":33.5,"lower_limit":33.5,"upper_limit":100.5}],
        [{"dose": 0 ,"time": 40 ,"response": 4,"n":20,"stdev":2,"lower_limit":2,"upper_limit":6},
        {"dose": 25 ,"time": 40 ,"response": 17,"n":20,"stdev":8.5,"lower_limit":8.5,"upper_limit":25.5},
        {"dose": 50 ,"time": 40 ,"response": 29,"n":20,"stdev":14.5,"lower_limit":14.5,"upper_limit":43.5},
        {"dose": 75 ,"time": 40 ,"response": 48,"n":20,"stdev":24,"lower_limit":24,"upper_limit":72},
        {"dose": 100 ,"time": 40 ,"response": 66,"n":20,"stdev":33,"lower_limit":33,"upper_limit":99}],
        [{"dose": 0 ,"time": 50 ,"response": 5,"n":20,"stdev":2.5,"lower_limit":2.5,"upper_limit":7.5},
        {"dose": 25 ,"time": 50 ,"response": 18,"n":20,"stdev":9,"lower_limit":9,"upper_limit":27},
        {"dose": 50 ,"time": 50 ,"response": 34,"n":20,"stdev":17,"lower_limit":17,"upper_limit":51},
        {"dose": 75 ,"time": 50 ,"response": 50,"n":20,"stdev":25,"lower_limit":25,"upper_limit":75},
        {"dose": 100 ,"time": 50 ,"response": 65,"n":20,"stdev":32.5,"lower_limit":32.5,"upper_limit":97.5}]
    ];

    this.colors = d3.scale.category10();
    colors_range = this.colors.range();

    $(this.dummy_values).each(function(i, v){
        y_max = Math.max(y_max, d3.max(v, function(d,i){return d.upper_limit;}));
        y_min = Math.min(y_min, d3.min(v, function(d,i){return d.lower_limit;}));
        $(v).each(function(i2, v2){v2.stroke = colors_range[i2];});
    });

    this.min_y = y_min;
    this.max_y = y_max*(1+this.buff);

    this.title_str = this.endpoint.data.name;
    this.x_label_text = "Time (hr)";
    this.y_label_text = "Response ({0})".printf(this.endpoint.data.response_units);
};

CTPlot.prototype.add_axes = function() {
    $.extend(this.x_axis_settings, {
        domain: this.dummy_values.map(function(d){return String(d[0].time);}),
        number_ticks: this.dummy_values.length,
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

CTPlot.prototype.add_lines = function(){
    var x = this.x_scale,
        y = this.y_scale,
        bar_offset = x.rangeBand()/2,
        colors = this.colors.range();

    this.time_paths = this.vis.append("g").attr('class', 'time_paths');

    var line = d3.svg.line()
        .x(function(d, i){return x(d.time)+bar_offset;})
        .y(function(d, i){return y(d.response);})
        .interpolate(["linear"]);

    this.time_paths.selectAll("text.ctlines")
        .data(d3.transpose(this.dummy_values))
        .enter().append("path")
        .attr("d", line)
        .attr('class','dr_line')
        .attr('stroke', function(v, i){ return colors[i];});
};

CTPlot.prototype.add_confidence_intervals = function(){

    var x = this.x_scale,
        y = this.y_scale,
        offset = x.rangeBand()/2,
        bar_spacing = x.rangeBand()*0.05;

    var colors = this.colors.range();

    this.time_uncertainty_bars = this.vis.append("g").attr('class', 'time_uncertainty_bars');

    var vals = d3.transpose(this.dummy_values);
    for(var j=0; j<vals.length; j++){
        this.time_uncertainty_bars.selectAll("svg.bars")
            .data(vals[j])
            .enter()
            .append("line")
                .attr("x1", function(d,i) {return x(d.time)+offset;})
                .attr("y1",  function(d) {return y(d.lower_limit);})
                .attr("x2", function(d,i) {return x(d.time)+offset;})
                .attr("y2", function(d) {return y(d.upper_limit);})
                .attr('stroke-width','2.0')
                .attr('stroke', function(v,i){return v.stroke;});

        this.time_uncertainty_bars.selectAll("svg.bars")
            .data(vals[j])
            .enter()
            .append("line")
                .attr("x1", function(d,i) {return x(d.time) + offset - bar_spacing;})
                .attr("y1",  function(d) {return y(d.lower_limit);})
                .attr("x2", function(d,i) {return x(d.time) + offset + bar_spacing;})
                .attr("y2", function(d) {return y(d.lower_limit);})
                .attr('stroke-width','2.0')
                .attr('stroke', function(v,i){return v.stroke;});


        this.time_uncertainty_bars.selectAll("svg.bars")
            .data(vals[j])
            .enter()
            .append("line")
                .attr("x1", function(d,i) {return x(d.time) + offset - bar_spacing;})
                .attr("y1",  function(d) {return y(d.upper_limit);})
                .attr("x2", function(d,i) {return x(d.time) + offset + bar_spacing;})
                .attr("y2", function(d) {return y(d.upper_limit);})
                .attr('stroke-width','2.0')
                .attr('stroke', function(v,i){return v.stroke;});
    }
};

CTPlot.prototype.add_legend = function(){
    // clear any existing legends
    // this.clear_legend();
    var r = this.colors.range();

    var legend_settings = {};
    legend_settings.items = [];
    $(this.dummy_values[0]).each(function(i, v){
        legend_settings.items.push({'text':v.dose + ' ' + endpoint.data.dose_units, 'classes':'', 'color': r[i]});
    });

    legend_settings.item_height = 20;
    legend_settings.box_w = 110;
    legend_settings.box_h = legend_settings.items.length*legend_settings.item_height;
    legend_settings.box_l = this.w - legend_settings.box_w-10;
    legend_settings.box_padding = 5;
    legend_settings.dot_r = 5;

    // determine if legend should go in top-right or bottom-right of plot.
    if (this.endpoint.dataset_increasing) {
        legend_settings.box_t = this.h-legend_settings.box_h - 20;
    } else {
        // legend_settings.box_t = 10;
        legend_settings.box_t = this.h-legend_settings.box_h - 20;
    }

    // build legend
    this.build_legend(legend_settings);
};

CTPlot.prototype.add_bmd_line = function(){};
