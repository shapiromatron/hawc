// Extend existing Endpoint object
Endpoint.prototype._percent_change_control = function(index){
    try{
        if (this.data.data_type == "C"){
            return this._continuous_percent_difference_from_control(
                this.data.endpoint_group[index],
                this.data.endpoint_group[0]);
        } else {
            return this._dichotomous_percent_change_incidence(this.data.endpoint_group[index]);
        }
    } catch(err){
        return '-';
    }
};

Endpoint.prototype.crossview_data_formatting = function(){
    // get metadata and an array of data-objects showing percent difference
    // from control
    var contents = [];
    for(var i=1; i<this.data.endpoint_group.length; i++){
        contents.push({
            'endpoint': this,
            'name': this.data.name,
            'study': this.data.animal_group.experiment.study.short_citation,
            'experiment': this.data.animal_group.experiment.name,
            'experiment_type': this.data.animal_group.experiment.type,
            'animal_group': this.data.animal_group.name,
            'dose': this.data.endpoint_group[i].dose,
            'change': this._percent_change_control(i)/100,
            'loael': this.data.LOAEL === i,
            'noael': this.data.NOAEL === i,
            'effects': this.data.effects.map(function(v){return v.name;}),
            'sex': this.data.animal_group.sex,
            'species': this.data.animal_group.species,
            'path_title': this.data.name
        });
    }
    return contents;
};

// Main plot object
var Crossview = function(endpoints, plot_div, settings){
    // Displays multiple-dose-response details on the same view and allows for
    // custom visualization of these plots
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.settings = settings || Crossview.default_settings();
    this.set_defaults();
    this.plottip = new PlotTooltip({"width": "500px", "height": "380px"});
    this.plot_div = $(plot_div);
    this.endpoints = endpoints; // expected array

    if(endpoints.length>0){
        if(this.settings.plot_settings.build_plot_startup){this.build_plot();}
    } else {
        this.plot_div.html("<p>Error- no endpoints found. Try selecting a different dose-unit.</p>");
    }
};

Crossview.prototype = new D3Plot();
Crossview.prototype.constructor = Crossview;

Crossview.default_settings = function(){
    return {
              "plot_settings": {
                "show_menu_bar": true,
                "build_plot_startup": true,
                "plot_width": 850,
                "text_width": 150,
                "height": 500,
                "padding": {
                  "top": 25,
                  "right": 50,
                  "bottom": 40,
                  "left": 70
                },
                "tag_height": 17,
                "tag_left_padding": 25,
                "tag_category_spacing": 5
              },
              "crossview_filters": [
                "study",
                "experiment_type",
                "species",
                "sex",
                "effects"
              ]
           };
};

Crossview.prototype.build_plot = function(){
    this.plot_div.html('');
    this.get_dataset();
    this.get_plot_sizes();
    this.build_plot_skeleton(false);
    this.add_axes();
    this.draw_visualizations();
    this.add_menu();
    this.add_title();
    this.build_x_label();
    this.build_y_label();
    this.trigger_resize();
};

Crossview.prototype.get_plot_sizes = function(){
    this.w = this.settings.plot_settings.plot_width + this.settings.plot_settings.text_width;
    this.h = this.settings.plot_settings.height;
    var menu_spacing = (this.settings.plot_settings.show_menu_bar) ? 40 : 0;
    this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
        menu_spacing) + 'px'});
};

Crossview.prototype.set_defaults = function(){
    this.padding = $.extend({}, this.settings.plot_settings.padding); //copy object
    this.padding.left_original = this.padding.left;

    var xlabel_format = d3.format(",.f"),
        ylabel_format = d3.format("%");

    this.x_axis_settings = {
        "scale_type": 'log',
        "text_orient": "bottom",
        "axis_class": 'axis x_axis',
        "gridlines": false,
        "gridline_class": 'primary_gridlines x_gridlines',
        "number_ticks": 10,
        "axis_labels": true,
        "label_format": xlabel_format
    };

    this.y_axis_settings = {
        'scale_type': "linear",
        'text_orient': "left",
        'axis_class': "axis y_axis",
        'gridlines': false,
        'gridline_class': "primary_gridlines y_gridlines",
        'number_ticks': 10,
        'axis_labels':true,
        'label_format': ylabel_format //default
    };
};

Crossview.prototype.get_dataset = function(){
    var dataset = [];

    this.endpoints.forEach(function(v,i){
        if(v.data.endpoint_group.length>0){
            dataset.push(v.crossview_data_formatting());
        }
    });

    var responses = dataset.map(
        function(v){
            return [
                d3.extent(v, function(v2){ return v2.dose;}),
                d3.extent(v, function(v2){ return v2.change;})
            ];
        });

    this.dose_range = [
        d3.min(responses, function(v){return v[0][0];}),
        d3.max(responses, function(v){return v[0][1];})
    ];
    this.response_range = [
        d3.min(responses, function(v){return v[1][0];}),
        d3.max(responses, function(v){return v[1][1];})
    ];
    this.dataset = dataset;

    this.title_str = '';
    this.x_label_text = "Dose ({0})".printf(this.endpoints[0].dose_units);
    this.y_label_text = '% change from control (continuous), % incidence (dichotomous)';
};

Crossview.prototype.add_axes = function() {
    $.extend(this.x_axis_settings, {
        "domain": this.dose_range,
        "rangeRound": [0, this.settings.plot_settings.plot_width],
        "x_translate": 0,
        "y_translate": this.h
    });

    $.extend(this.y_axis_settings, {
        "domain": this.response_range,
        "number_ticks": 10,
        "rangeRound": [this.h, 0],
        "x_translate": 0,
        "y_translate": 0
    });

    this.build_y_axis();
    this.build_x_axis();
};

Crossview.prototype.draw_visualizations = function(){
    var x = this.x_scale,
        y = this.y_scale,
        self = this;

    // reference line
    this.reference_lines = this.vis.append("g");
    this.reference_lines.selectAll("svg.endpoint_lines")
        .data([{}])
      .enter().append("line")
        .attr("x1", function(d) { return x(x.domain()[0]); })
        .attr("y1", function(d) { return y(0); })
        .attr("x2", function(d) { return x(x.domain()[1]); })
        .attr("y2", function(d) { return y(0); })
        .attr('class','primary_gridlines');

    //response-lines
    this.response_centerlines = this.vis.append("g");
    var line = d3.svg.line()
        .interpolate("basis")
        .x(function(d){return x(d.dose);})
        .y(function(d){return y(d.change);});

    this.response_centerlines.selectAll(".crossview_paths")
        .data(this.dataset)
      .enter().append("path")
        .attr("class", "crossview_paths")
        .attr("d", line)
        .on('click', function(v){self.plottip.display_endpoint(v[0].endpoint, d3.event);})
        .on('mouseover', function(v){self.change_show_selected_fields(this, v, true);})
        .on('mouseout', function(v){self.change_show_selected_fields(this, v, false);});

    d3.selectAll(".crossview_paths").append("svg:title")
        .text(function(v){return v[0].path_title;});


    // Set default crossview filters
    var filters = [];
    this.settings.crossview_filters.forEach(function(field){
        filters.push(self.build_crossview(field));
    });
    this.filters = filters;
    this.active_filters = [];
    this.hover_filter = undefined;

    // now add each field
    this.crossviews_g = this.vis.append("g");
    var height = -this.settings.plot_settings.tag_height,
        tag_x = self.settings.plot_settings.plot_width + self.settings.plot_settings.tag_left_padding,
        tag_y = function(){height += self.settings.plot_settings.tag_height; return height;};
    this.filters.forEach(function(crossview){
        // print header
        self.crossviews_g
            .append('text')
            .attr("x", tag_x)
            .attr("y", function(){return tag_y();})
            .attr("text-anchor", "start")
            .attr('class', 'crossview_title')
            .text(crossview[0].field);

        //print fields
        self.crossviews_g.selectAll("crossview.texts")
            .data(crossview)
        .enter().append("text")
            .attr("x", tag_x)
            .attr("y", function(){return tag_y();})
            .attr("text-anchor", "start")
            .attr('class', 'crossview_fields')
            .text(function(v) {return v.text;})
            .on('click', function(v){self.change_active_filters(v, this);})
            .on('mouseover', function(v){self.change_hover_filter(v, this);})
            .on('mouseout', function(v){self.change_hover_filter(v, this);});
        height += self.settings.plot_settings.tag_category_spacing;
    });
};

Crossview.prototype.change_show_selected_fields = function(path, v, hover_on){
    // if a user hovers over an object, highlight all crossviews that item
    // belongs to.

    // fix IE bug with mouseover events: http://stackoverflow.com/questions/3686132/
    if (hover_on && d3.select(path).classed('crossview_path_hover')) return;

    // only show if the field is a selected subset, if selected subset exists
    if ((this.crossview_selected) &&
        (!d3.select(path).classed('crossview_selected'))){return;}

    d3.select(path).classed('crossview_path_hover', hover_on).moveToFront();
    d3.selectAll('.crossview_fields').classed('crossview_path_hover', false);
    if(hover_on){
        d3.selectAll('.crossview_fields').each(function(filter){
            if(Crossview._filter_match(v[0][filter.field], filter.text)){
                d3.select(this).classed('crossview_path_hover', true);
            }
        });
    }
};

Crossview.prototype.change_active_filters = function(v, text){
    var active_filter = true;
    // check if filter already on; if on then turn off, else add
    if(this.active_filters.length>=1){
        for (var i = this.active_filters.length - 1; i >= 0; i -= 1){
            if(this.active_filters[i] === v){active_filter = false; this.active_filters.splice(i, 1);}
        }
    }
    if (active_filter){this.active_filters.push(v);}
    d3.select(text).classed('crossview_selected', active_filter)
                   .classed('crossview_hover', false);
    this._update_selected_filters();
};

Crossview.prototype.change_hover_filter = function(v, text){
    if (this.hover_filter === v){
        this.hover_filter = undefined;
        d3.select(text).classed('crossview_hover', false);
    } else {
        this.hover_filter = v;
        d3.select(text).classed('crossview_hover', true);
    }
    this._update_hover_filters();
};

Crossview.prototype.build_crossview = function(field){

    var sort_unique = function(arr) {
        arr = arr.sort(function (a, b){return b < a ? 1 : -1;});
        var ret = [arr[0]];
        for (var i = 1; i < arr.length; i++) { // start loop at 1 as element 0 can never be a duplicate
            if (arr[i-1] !== arr[i]) {
                ret.push(arr[i]);
            }
        }
        return ret;
    }, cross_view_list = [], values;

    // extract values in array
    if (Crossview.isArray(this.dataset[0][0][field])){
        values = [];
        this.dataset.forEach(function(v){
            values = values.concat(v[0][field]);
        });
    } else {
        values = this.dataset.map(function(v){return v[0][field];});
    }
    values = sort_unique(values);

    values.forEach(function(value){
        cross_view_list.push({'field': field,
                              'status':false,
                              'text': value});
    });

    return cross_view_list;
};

Crossview.prototype._update_selected_filters = function(){
    d3.selectAll('.crossview_paths')
        .classed('crossview_selected', false);

    var sel = d3.selectAll('.crossview_paths');
    if(this.active_filters.length>0){
        this.active_filters.forEach(function(filter){
            sel = sel.filter(function(d){return Crossview._filter_match(d[0][filter.field], filter.text);});
        });
        sel.classed('crossview_selected', true).moveToFront();
    }
    this.crossview_selected = sel;
    this._update_hover_filters();
};

Crossview.prototype._update_hover_filters = function(){
    var sel = this.crossview_selected || d3.selectAll('.crossview_paths'),
        filter = this.hover_filter;
    d3.selectAll('.crossview_paths').classed('crossview_hover', false);
    if(filter){
        sel.filter(function(d){return Crossview._filter_match(d[0][filter.field], filter.text);})
            .classed('crossview_hover', true)
            .moveToFront();
    }
};

d3.selection.prototype.moveToFront = function(){
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};

Crossview.isArray = function(obj){
    return (Object.prototype.toString.call(obj) === '[object Array]');
};

Crossview._filter_match = function(value, text){
    // filter which will return true if a match is found, false if otherwise.
    // Value can either be a singular value or an array.  Text is a single-value.
    if(Crossview.isArray(value)){
        var match = false;
        value.forEach(function(item){
            if(item===text){match=true; return;}
        });
        return match;
    } else {
        return value === text;
    }
};
