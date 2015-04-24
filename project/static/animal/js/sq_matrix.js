StudyQualityMatrix = function(aggregation, plot_id, options, parent){
    D3Plot.call(this); // call parent constructor
    this.aggregation = aggregation;
    this.plot_div = $(plot_id);
    this.options = options;
    this.parent = parent;
    this.set_defaults(options);
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(StudyQualityMatrix.prototype, D3Plot.prototype, {
    set_defaults: function(options){
        this.padding = {top:40, right:30, bottom:40, left:510};
        this.buff = 0.05; // addition numerical-spacing min/max
        this.score_width = 30;
        this.gradient_colors = d3.scale.linear() // should be consistent with endpoint.js StudyConfidenceTable
            .domain([1, 2, 3, 4])
            .range(["#CC3333", "#FFCC00", "#6FFF00", "#00CC00"]);

        var formatNumber = d3.format(",.f");

        this.x_axis_settings = {
            'scale_type': 'log',
            'text_orient': 'bottom',
            'x_translate': 0,
            'axis_class': 'axis x_axis',
            'gridlines': true,
            'gridline_class': 'primary_gridlines x_gridlines',
            'number_ticks': 10,
            'axis_labels': true,
            'label_format': formatNumber
        };

        this.y_axis_settings = {
            'scale_type': 'ordinal',
            'text_orient': "left",
            'y_translate': 0,
            'axis_class': 'axis y_axis',
            'gridlines': true,
            'gridline_class': 'primary_gridlines x_gridlines',
            'axis_labels': true,
            'label_format': undefined //default
        };
    },
    build_plot: function(){
        this.plot_div.html('');
        this.get_dataset_info();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.draw_visualizations();
        this.build_labels_information();
        this.build_x_label();
        this.customize_menu();
        this.trigger_resize();
    },
    customize_menu: function(){
        this.add_menu();
        if (this.parent){this.parent.add_toggle_button(this);}
    },
    get_dataset_info: function(){

        // get datasets to plot
        var points = [],
            lines = [],
            overall_study_confidence = [],
            score_width = this.score_width,
            gradient_colors = this.gradient_colors;

        this.aggregation.endpoints.forEach(function(v1, i1){

            //setup lines information for dose-response line (excluding control)
            lines.push({y: v1.data.name,
                        x_lower: v1.data.dr[1].dose,
                        x_upper: v1.data.dr[v1.data.dr.length-1].dose});

            // add dose points
            v1.data.dr.forEach(function(v2,i2){
                txt = [v1.data.study,
                       v1.data.name,
                       'Dose: ' + v2.dose,
                       'N: ' + v2.n];
                if (v2.dose>0){
                    if (v1.data.data_type == 'C'){
                        txt.push('Mean: ' + v2.response, 'Stdev: ' + v2.stdev);
                    } else {
                        txt.push('Incidence: ' + v2.incidence);
                    }
                    coords = {endpoint: v1,
                              x: v2.dose,
                              y: v1.data.name,
                              classes:'',
                              text: txt.join('\n')};
                    if (v1.data.LOEL == i2){ coords.classes='LOEL';}
                    if (v1.data.NOEL == i2){ coords.classes='NOEL';}
                    points.push(coords);
                }
            });

            // add BMDL
            if (isFinite(v1.get_bmd_special_values('BMDL'))) {
                txt = [v1.data.study,
                       v1.data.name,
                       'BMD Model: ' + v1.data.BMD.outputs.model_name,
                       'BMD: ' + v1.data.BMD.outputs.BMD + ' (' + v1.data.dose_units + ')',
                       'BMDL: ' + v1.data.BMD.outputs.BMDL + ' (' + v1.data.dose_units + ')'];
                points.push({endpoint: v1,
                                  x: v1.get_bmd_special_values('BMDL'),
                                  y: v1.data.name,
                                  classes: 'BMDL',
                                  text : txt.join('\n')});
            }

            // add overall score fields
            v1.data.study_confidence.forEach(function(v2, i2){
                // individual description
                var desc = $('<div></div>'),
                    ol = $('<ol class="score-details"></ol>');
                v2.individual.forEach(function(v3){
                    var div = $('<div class="heatmap_selectable">' + v3.score + '</div>').css("background", gradient_colors(v3.score));
                    ol.append($('<li></li>').append(div).append(v3.criterion));
                });
                desc.append(ol);
                overall_study_confidence.push({
                    x: i2 * score_width,
                    y: v1.data.name,
                    score: v2.score,
                    scoretext: v2.scoretext,
                    label: v2.domain,
                    fill: gradient_colors(v2.score),
                    description: desc.html(),
                    endpoint: v1
                });
            });
        });

        this.points = points;
        this.lines = lines;
        this.number_score_categories = this.aggregation.endpoints[0].data.study_confidence.length;
        this.overall_study_confidence = overall_study_confidence;

        // get axis bounds
        this.min_x = d3.min(lines, function(v){return v.x_lower;});
        this.max_x = d3.max(lines, function(v){return v.x_upper;});

        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
        this.h = this.lines.length*30;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});

        this.title_str = "Example comparative mockup of critical values";
        this.x_label_text = "Dose (mg/kg/day)";
        this.y_label_text = "y label axis name";
    },
    add_axes: function(){
        $.extend(this.x_axis_settings, {
            domain: [this.min_x, this.max_x],
            rangeRound: [0, this.w],
            y_translate: this.h });

        this.y_axis_offset = this.number_score_categories * this.score_width * -1;

        $.extend(this.y_axis_settings, {
            domain: this.aggregation.endpoints.map(function(d){return d.data.name;}),
            number_ticks: this.aggregation.endpoints.length,
            x_translate: this.y_axis_offset - 10,
            rangeRound: [this.h, 0]
        });

        this.build_x_axis();
        this.build_y_axis();
    },
    build_labels_information: function(){
        this.add_title();
        // this.build_x_label();
        // this.build_y_label();
        this.add_final_rectangle();
    },
    draw_visualizations: function(){
        // horizontal line separators between endpoints
        var x = this.x_scale,
            y = this.y_scale,
            gradient_colors = this.gradient_colors,
            half_y = y.rangeBand()/2.0,
            score_width = this.score_width;

        //dose-range lines
        this.dosing_lines = this.vis.append("g");
        var bar_options = {
            data: this.lines,
            x1: function(d) {return x(d.x_lower);},
            y1: function(d) {return y(d.y) + half_y;},
            x2: function(d) {return x(d.x_upper);},
            y2: function(d) {return y(d.y) + half_y;},
            classes: 'dr_err_bars',
            append_to: this.dosing_lines
        };
        this.dosing_lines = this.build_line(bar_options);

        // dose-points
        this.dots_group = this.vis.append("g");
        this.dots = this.dots_group.selectAll("path.dot")
            .data(this.points)
          .enter().append("circle")
            .attr("r", "7")
            .attr("class", function(d){ return "dose_points " + d.classes;})
            .attr("transform", function(d) {
                return "translate(" + x(d.x)  + "," +
                        (y(d.y) + half_y) + ")"; });
        this.dots.append("svg:title").text(function(d) { return d.text; });

        // study confidence rectangles
        var width = this.y_axis_offset - 5;
        this.overall_study_confidence_group = this.vis.append("g");
        this.overall_study_confidence_rect = this.overall_study_confidence_group.selectAll("*")
            .data(this.overall_study_confidence)
            .enter().append("rect")
            .attr("x", function(d){return width+d.x;})
            .attr("y", function(d){return y(d.y)+half_y-score_width/2;})
            .attr("width", this.score_width)
            .attr("height", this.score_width)
            .attr("class", "heatmap_selectable")
            .style("fill", function(d){return d.fill;})
            .on('click', function(d){
                new EndpointDetailRow(d.endpoint, "#endpoint_details", 0, {show_study_details: true});
            })
            .on('mouseover', function(d){
                plot.show_tooltip(d.label, d.description);
            })
            .on('mouseout', function(){
                plot.hide_tooltip();
            });

        this.overall_study_confidence_lbl = this.overall_study_confidence_group.selectAll("text")
            .data(this.overall_study_confidence)
            .enter().append("text")
            .attr("x", function(d){return width + d.x + score_width/2;})
            .attr("y", function(d){return y(d.y) + half_y+4;})
            .attr("class", "uf_label")
            .text(function(d){return d.scoretext;});
    }
});
