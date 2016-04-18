var RiskOfBiasCollection = function(objs){
    this.object_list = objs;
};
_.extend(RiskOfBiasCollection, {
    get_list: function(id, cb){
        $.get('/study/api/study/?assessment_id={0}'.printf(id), function(ds){
            var objs = _.map(ds, function(d){ return new RiskOfBiasStudy(d); });
            cb(new RiskOfBiasCollection(objs));
        });
    },
    render: function(id, $div){
        RiskOfBiasCollection.get_list(id, function(d){d.render($div);});
    },
});
RiskOfBiasCollection.prototype = {
    render: function($el){
        $el.hide()
            .append(this.build_filters())
            .append(this.build_table())
            .fadeIn();

        this.registerEvents($el);
    },
    build_filters: function(){
        var $el = $('<div class="row-fluid">'),
            filters = _.chain(this.object_list)
                       .map(function(d){return d.data.study_type;})
                       .uniq()
                       .value();

        if (filters.length>1){
            $el.html(
                $('<select class="span12" size="6" multiple>').html(_.map(filters, function(d){
                    return '<option value="{0}" selected>{0}</option>'.printf(d);
                }))
            );
        }
        return $el;
    },
    build_table: function(){
        var self = this,
            tbl = new BaseTable(),
            colgroups = [25, 60, 15],
            header = ['Short citation', 'Full citation', 'Study type'];

        tbl.addHeaderRow(header);
        tbl.setColGroup(colgroups);

        _.each(this.object_list, function(d){
            tbl.addRow(d.build_row()).data('obj', d);
        });

        return tbl.getTbl();
    },
    registerEvents: function($el){
        var trs = _.map($el.find('table tbody tr'), $),
            vals;
        $el.find('select').on('change', function(e){
            vals = $(this).val();
            _.each(trs, function(tr){
                tr.toggle(vals.indexOf(tr.data('obj').data.study_type)>=0);
            });
        });
    },
};

var RiskOfBiasStudy = function(data){
    this.data = data;
};
RiskOfBiasStudy.prototype = {
    get_url: function(){
        return '<a href="/rob{0}">{1}</a>'.printf(this.data.url, this.data.short_citation);
    },
    build_row: function(){
        return [this.get_url(), this.data.full_citation, this.data.study_type];
    },
};

var RiskOfBias_TblCompressed = function(study, div, options){
    this.study = study;
    this.$div = $(div);
    this.build_table();

    if (options && options.show_all_details_startup){
        this.show_details_div();
    }
};

var RiskOfBias = function(study, data){
    this.study = study;
    this.data = data;
    this.data.metric.created = new Date(this.data.metric.created);
    this.data.metric.last_updated = new Date(this.data.metric.last_updated);
};

_.extend(RiskOfBias, {
    score_values: [0, 1, 2, 3, 4],
    score_text: {0: 'N/A', 1: '--', 2: '-', 3: '+', 4: '++'},
    score_shades: {0: "#E8E8E8", 1: "#CC3333", 2: "#FFCC00", 3: "#6FFF00", 4: "#00CC00"},
    score_text_description: {
        0: 'Not applicable',
        1: 'Definitely high risk-of-bias',
        2: 'Probably high risk-of-bias',
        3: 'Probably low risk-of-bias',
        4: 'Definitely low risk-of-bias',
    },
    display_details_divs: function($div, content){
        // insert content into selected div and then draw all animations
        // associated with this insertion.
        $(":animated").promise().done(function() {
            $div.html(content);
            $div.fadeIn();
        }, function(){
            $('.rob_score_bar').each(function(){
                $(this).data('animate')();
            });
        });
    },
    build_study_comparison_div: function(robs){
        // construct a div which compares one metric across multiple studies.
        // This expects an array of study-quality objects where each object is
        // a different study but ALL objects are the same metric.
        var content = ['<hr><h3>{0}</h3>'.printf(robs[0].data.metric.domain.name),
                       '<h4>{0}</h4>'.printf(robs[0].data.metric.metric),
                       '<div class="help-block">{0}</div>'.printf(robs[0].data.metric.description)];
        robs.forEach(function(rob){
            content.push('<h4><a target="_blank" href="{0}">{1}</a></h4>'.printf(rob.study.data.url, rob.study.data.short_citation),
                         rob._build_details_div());
        });
        return $('<div class="row-fluid"></div>').html(content);
    },
    build_metric_comparison_div: function(robs){
        // construct a div which compares one study across multiple metrics.
        // This expects an array of study-quality objects where each object is
        // a different metric but ALL objects are the same study.
        var domain_text,
            content = [];
        robs.forEach(function(rob){
            if(rob.data.metric.domain.name !== domain_text){
                content.push('<hr><h3>{0}</h3>'.printf(rob.data.metric.domain.name));
                domain_text = rob.data.metric.domain.name;
            }
            content.push('<h4>{0}</h4>'.printf(rob.data.metric.metric),
                         '<div class="help-block">{0}</div>'.printf(rob.data.metric.description),
                         rob._build_details_div());
        });
        return $('<div class="row-fluid"></div>').html(content);
    }
});

RiskOfBias.prototype = {
    build_details_div: function(options){
        var content = [];
        options = options || {};
        if (options.show_study){
            content.push('<h3><a href="{0}">{1}</a>: {2}</h3>'.printf(this.study.data.url,
                                                                      this.study.data.short_citation,
                                                                      this.data.metric.domain.name));
        } else {
            content.push('<h3>{0}</h3>'.printf(this.data.metric.domain.name));
        }
        content.push('<h4>{0}</h4>'.printf(this.data.metric.metric),
                     '<div class="help-block">{0}</div>'.printf(this.data.metric.description),
                     this._build_details_div());
        return $('<div class="row-fluid"></div>').html(content);
    },
    _build_details_div: function(){
        // constructs and returns a div which presents an animated score-field and a
        // description of the associated score.
        var $div = $('<div class="row-fluid"></div>'),
            score_div = $('<div class="span3"></div>'),
            description_div = $('<div class="span9">{0}</div>'.printf(this.data.notes));

        $div.append($('<div class="row-fluid"></div>').html([score_div, description_div]));
        var bar_width = d3.max([d3.round(this.data.score / 4 * 100, 2), 15]),
            rob_score_bar = $('<div class="rob_score_bar" style="width:15%; background-color:{0};"><span style="padding-right:5px">{1}</span></div>'.printf(this.data.score_color, this.data.score_text))
                .data('animate', function(){
                    $(rob_score_bar).animate({'width': bar_width + '%'}, 500);});
        score_div.append([rob_score_bar, '<p>{0}</p>'.printf(this.data.score_description)]);
        return $div;
    }
};


RiskOfBias_TblCompressed.prototype = {
    build_table: function(){
        var self = this;
        this.tbl = $('<table class="table table-condensed"></table>');
        this.build_tbody();
        this.build_footer();
        this.selected_div = $('<div style="display:none"></div>');
        this.$div.html([this.tbl, this.selected_div]);
        $(".tooltips").tooltip();
        $('.rob_criteria').on('click', 'td', function(){self.show_details_div(this);});
        $('.rob_domains').on('click', 'td', function(){self.show_details_div(this);});
    },
    show_details_div: function(selected){
        var $sel = $(selected),
            divs = [],
            self = this,
            show_all_text = 'Show all details';

        this.selected_div.fadeOut();

        if ($sel.data('robs')){
            divs.push(RiskOfBias.build_metric_comparison_div($sel.data('robs').criteria));
        } else if ($sel.data('rob')) {
            divs.push($sel.data('rob').build_details_div());
        } else {
            // show all details
            selected = this.study;
            this.study.riskofbias.forEach(function(v1, i1){
                divs.push(RiskOfBias.build_metric_comparison_div(v1.criteria));
            });
            show_all_text = 'Hide all details';
        }
        divs.push(
            $('<hr><a href="#" class="btn btn-small"><i class="icon-plus"></i> {0}</a>'.printf(show_all_text)).click(
                function(e){e.preventDefault(); self.show_details_div();}));

        if (this.selected === selected){
            this.selected = undefined;
        } else {
            this.selected = selected;
            RiskOfBias.display_details_divs(self.selected_div, divs);
        }
    },
    build_tbody: function(){
        var tbody = $('<tbody></tbody>'),
            tr1 = $('<tr class="rob_domains"></tr>'),
            tr2 = $('<tr class="rob_criteria"></tr>');
        this.study.riskofbias.forEach(function(v1, i1){
            v1.criteria.forEach(function(v2, i2){
                if(i2 === 0){
                    tr1.append($('<td class="scorecell domain_cell" colspan="{0}">{1}</td>'.printf(
                                 v1.criteria.length,
                                 v1.domain_text)).data('robs', v1));
                }
                tr2.append($('<td class="scorecell" style="background-color: {0};"><span class="tooltips" data-toggle="tooltip" title="{1}">{2}</span></td>'.printf(
                                v2.data.score_color,
                                v2.data.metric.metric,
                                v2.data.score_text)).data('rob', v2));
            });
        });
        this.num_cols = tr2.children().length;
        this.tbl.append(tbody.append(tr1, tr2));
    },
    build_footer: function(){
        var tfoot = $('<tfoot>'),
            txt = 'Click on any cell above to view details.';
        tfoot.append($('<tr>').append(
            $('<td>').text(txt).attr({'colspan': this.num_cols, 'class': 'muted'})));
        this.tbl.prepend(tfoot);
    }
}



var RiskOfBias_Donut = function(study, plot_id, options){
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.study = study;
    this.plot_div = $(plot_id);
    this.options = options;
    this.viewlock = false;
    if(!this.study.riskofbias || this.study.riskofbias.length === 0 ) return;
    this.set_defaults(options);
    if(this.options && this.options.build_plot_startup){this.build_plot();}
    $('body').on('keydown', function() {
        if (event.ctrlKey || event.metaKey){self.toggle_lock_view();}
    });
};
_.extend(RiskOfBias_Donut.prototype, D3Plot.prototype, {
    set_defaults: function(options){
        this.w = 800;
        this.h = 400;
        this.radius_inner = 30;
        this.radius_middle = 150;
        this.radius_outer = 200;
        this.padding = {top:10, right:10, bottom:10, left:10};
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
    },
    build_plot: function(){
        this.plot_div.html('');
        this.get_dataset_info();
        this.build_plot_skeleton(false);
        this.draw_visualizations();
        this.customize_menu();
        this.trigger_resize();
    },
    customize_menu: function(){
        this.add_menu();
        var plot = this;
        var options = {id:'lock_view',
                       cls: 'btn btn-mini',
                       title: 'Lock current view (shortcut: press ctrl to toggle)',
                       text: '',
                       icon: 'icon-lock',
                       on_click: function(){plot.toggle_lock_view();}};
       this.add_menu_button(options);
    },
    toggle_lock_view: function(){
        this.plot_div.find('#lock_view').toggleClass("btn-info");
        this.viewlock = !this.viewlock;
    },
    get_dataset_info: function(){

        var domain_donut_data = [],
            question_donut_data = [];

        this.study.riskofbias.forEach(function(v1){
            domain_donut_data.push({weight:10, // equally weighted
                                    score: v1.score,
                                    score_text: v1.score_text,
                                    score_color: v1.score_color,
                                    score_text_color: String.contrasting_color(v1.score_color),
                                    domain: v1.domain_text,
                                    self: v1});
            v1.criteria.forEach(function(v2){
                question_donut_data.push({weight:10/v1.criteria.length,
                                    score: v2.data.score,
                                    score_text: v2.data.score_text,
                                    score_color: v2.data.score_color,
                                    score_text_color: v2.data.score_text_color,
                                    criterion: v2.data.metric.metric,
                                    notes: v2.data.notes,
                                    parent: v1});
            });
        });
        this.domain_donut_data = domain_donut_data;
        this.question_donut_data = question_donut_data;
    },
    draw_visualizations: function(){
        var self = this,
            donut_center = "translate(" + (200) + "," + (this.h / 2) + ")";

        // setup pie layout generator
        this.pie_layout = d3.layout.pie()
          .sort(null)
          .value(function(d) { return d.weight; });

        // setup arc helper functions
        var domain_arc = d3.svg.arc()
                .innerRadius(this.radius_inner)
                .outerRadius(this.radius_outer),
            details_arc = d3.svg.arc()
                .innerRadius(this.radius_middle)
                .outerRadius(this.radius_outer);

        this.domain_outer_radius = this.radius_outer;
        this.details_arc = details_arc;
        this.domain_arc = domain_arc;

        // setup groups
        this.detail_arc_group = this.vis.append("g")
          .attr("transform", donut_center);

        this.detail_label_group = this.vis.append("g")
          .attr("transform", donut_center);

        this.domain_arc_group = this.vis.append("g")
          .attr("transform", donut_center);

        this.domain_label_group = this.vis.append("g")
          .attr("transform", donut_center);

        // add domain labels. Two sets because we want two rows of information
        this.domain_domain_labels = this.domain_label_group.selectAll("text1")
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append("text")
                .attr("class", "centeredLabel domain_arc")
                .attr("transform", function(d) { return "translate(" + (domain_arc.centroid(d)) + ")"; })
                .attr("text-anchor", "middle")
                .text(function(d) { return d.data.domain; });

        this.domain_score_labels = this.domain_label_group.selectAll("text2")
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append("text")
                .attr("class", "centeredLabel")
                .style("fill",  function(d){return d.data.score_text_color;})
                .attr("transform", function(d){
                    var centroid = domain_arc.centroid(d);
                    return "translate(" + [centroid[0],centroid[1]+15] + ")";})
                .attr("text-anchor", "middle");

        // add detail labels
        this.detail_labels = this.detail_label_group.selectAll("text")
            .data(this.pie_layout(this.question_donut_data))
            .enter().append("text")
            .attr("class", "centeredLabel")
            .style("fill",  function(d){return d.data.score_text_color;})
            .attr("transform", function(d) { return "translate(" + (details_arc.centroid(d)) + ")"; })
            .attr("text-anchor", "middle")
            .text(function(d) { return d.data.score_text; });

        // add detail arcs
        var detail_arcs = this.detail_arc_group.selectAll("path")
                .data(this.pie_layout(this.question_donut_data))
            .enter()
                .append("path")
                .attr("fill", function(v){return v.data.score_color;})
                .attr("class", "donuts metric_arc")
                .attr("d", details_arc)
                .on('mouseover', function(v1){
                    if (self.viewlock) return;
                    d3.select(this).classed("hovered", true);
                    $(":animated").promise().done(function(){
                        self.show_subset(v1.data);
                    });
                })
                .on('mouseout', function(v){
                    if (self.viewlock) return;
                    d3.select(this).classed("hovered", false);
                    detail_arcs.classed("hovered", false);
                    domain_arcs.classed("hovered", false);
                    self.subset_div.fadeOut("500", function(){self.clear_subset();});
                });
        this.detail_arcs = detail_arcs;

        // add domain arcs
        var domain_arcs = this.domain_arc_group.selectAll("path")
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append("path")
                .attr("class", "donuts domain_arc")
                .attr("d", domain_arc);
        this.domain_arcs = domain_arcs;

        // build plot div, but make hidden by default
        this.subset_div = $('<div></div>')
            .css({'position':'relative',
                  'display' : 'none',
                  'height': -this.h - this.padding.top - this.padding.bottom,
                  'padding': '5px',
                  'width': this.w/2 - this.padding.left - this.padding.right,
                  'left' : this.w/2 + this.padding.left + this.padding.right + 10,
                  'top': -this.h + this.padding.top + 10});
        this.plot_div.append(this.subset_div);

        // print title
        this.title = this.vis.append("svg:text")
            .attr("x", this.w)
            .attr("y", this.h)
            .attr("text-anchor", "end")
            .attr("class","dr_title")
            .text('{0} risk-of-bias summary'.printf(this.study.data.short_citation));

        setTimeout(function(){self.toggle_domain_width();}, 2.0);
    },
    toggle_domain_width: function(){
        var new_radius = this.radius_middle;
        if (this.domain_outer_radius === this.radius_middle)
            new_radius = this.radius_outer;

        this.domain_arc = d3.svg.arc()
            .innerRadius(this.radius_inner)
            .outerRadius(new_radius);
        this.domain_outer_radius = new_radius;

        this.domain_arcs
            .transition()
            .duration("500")
            .attr('d', this.domain_arc);

        var domain_arc = this.domain_arc;
        this.domain_domain_labels
            .transition()
            .duration("500")
            .attr("transform", function(d) { return "translate(" + (domain_arc.centroid(d)) + ")"; });
        this.domain_score_labels
            .transition()
            .duration("500")
            .attr("transform", function(d){
                    var centroid = domain_arc.centroid(d);
                    return "translate(" + [centroid[0],centroid[1]+15] + ")";});
    },
    clear_subset: function(){
      this.subset_div.empty();
    },
    show_subset: function(metric){
        this.clear_subset();
        this.subset_div.append('<h4>{0} domain</h4>'.printf(metric.parent.domain_text));
        var ol = $('<ol class="score-details"></ol>'),
            div = $('<div>').text(metric.score_text)
                            .attr('class', 'scorebox')
                            .css("background", metric.score_color),
            metric_txt = $('<b>').text(metric.criterion),
            notes_txt = $('<p>').html(metric.notes);
        ol.append($('<li>').html([div, metric_txt, notes_txt]));
        this.subset_div.append(ol);
        this.subset_div.fadeIn("500");
    }
});

var RiskOfBiasAggregation = function(studies){
    this.studies = studies;
    this.metrics_dataset = this.build_metrics_dataset();
};

RiskOfBiasAggregation.prototype = {
    build_metrics_dataset: function(){
        var arr = [];
        this.studies.forEach(function(study){
            study.riskofbias.forEach(function(domain){
                domain.criteria.forEach(function(rob){
                    arr.push(rob);
                });
            });
        });

        var ds = d3.nest()
                    .key(function(d){return d.data.metric.id;})
                    .entries(arr);

        var score_binning = function(d){
            var score_bins = {'0': {rob_scores:[], score:0, score_text:'N/A', score_description: 'Not applicable'},
                              '1': {rob_scores:[], score:1, score_text:'--', score_description: 'Definitely high risk-of-bias'},
                              '2': {rob_scores:[], score:2, score_text:'-', score_description: 'Probably high risk-of-bias'},
                              '3': {rob_scores:[], score:3, score_text:'+', score_description: 'Probably low risk-of-bias'},
                              '4': {rob_scores:[], score:4, score_text:'++', score_description: 'Definitely low risk-of-bias'}};
            d.rob_scores.forEach(function(rob){
                score_bins[rob.data.score].rob_scores.push(rob);
            });
            return score_bins;
        };

        ds.forEach(function(v){
            v.rename_property('key', 'domain');
            v.rename_property('values', 'rob_scores');
            v.domain_text = v.rob_scores[0].data.metric.domain.name;
            var possible_score = d3.sum(v.rob_scores.map(function(v){return (v.data.score>0)?4:0;})),
                score = d3.sum(v.rob_scores.map(function(v){return v.data.score;}));
            v.score = (possible_score>0)?d3.round(score/possible_score*100, 2):0;
            v.score_bins = score_binning(v);
        });
        return ds;
    }
};
