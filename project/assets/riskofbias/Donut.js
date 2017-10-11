import $ from '$';
import d3 from 'd3';

import D3Plot from 'utils/D3Plot';


class Donut extends D3Plot {

    constructor(study, plot_id, options){
        super();
        var self = this;
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
    }

    set_defaults(options){
        this.w = 800;
        this.h = 400;
        this.radius_inner = 30;
        this.radius_middle = 150;
        this.radius_outer = 200;
        this.padding = {top:10, right:10, bottom:10, left:10};
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom) + 'px'});
    }

    build_plot(){
        this.plot_div.html('');
        this.get_dataset_info();
        this.build_plot_skeleton(false);
        this.draw_visualizations();
        this.customize_menu();
        this.trigger_resize();
    }

    customize_menu(){
        this.add_menu();
        var plot = this;
        var options = {id:'lock_view',
                       cls: 'btn btn-mini',
                       title: 'Lock current view (shortcut: press ctrl to toggle)',
                       text: '',
                       icon: 'icon-lock',
                       on_click(){plot.toggle_lock_view();}};

        this.add_menu_button(options);
    }

    toggle_lock_view(){
        this.plot_div.find('#lock_view').toggleClass('btn-info');
        this.viewlock = !this.viewlock;
    }

    get_dataset_info(){

        var domain_donut_data = [],
            question_donut_data = [];
			
        this.study.riskofbias.forEach(function(v1, idx){
            domain_donut_data.push({weight:10, // equally weighted
                                    score: v1.score,
                                    score_text: v1.score_text,
                                    score_color: v1.score_color,
                                    score_text_color: String.contrasting_color(v1.score_color),
                                    domain: v1.domain_text,
									idxOrder:idx,
                                    self: v1});
            v1.criteria.forEach(function(v2){
                question_donut_data.push({weight:10/v1.criteria.length,
                                    score: v2.data.score,
                                    score_text: v2.data.score_text,
                                    score_color: v2.data.score_color,
                                    score_text_color: v2.data.score_text_color,
                                    criterion: v2.data.metric.name,
                                    notes: v2.data.notes,
                                    parent: v1});
            });
        });
        this.domain_donut_data = domain_donut_data;
        this.question_donut_data = question_donut_data;
    }

    draw_visualizations(){
        var self = this,
            donut_center = `translate(200,${(this.h / 2)})`;

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
        this.detail_arc_group = this.vis.append('g')
          .attr('transform', donut_center);

        this.detail_label_group = this.vis.append('g')
          .attr('transform', donut_center);

        this.domain_arc_group = this.vis.append('g')
          .attr('transform', donut_center);

        this.domain_label_group = this.vis.append('g')
          .attr('transform', donut_center);

        // add domain labels. Two sets because we want two rows of information
        this.domain_domain_labels = this.domain_label_group.selectAll('text1')
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append('text')
                .attr('class', 'centeredLabel domain_arc')
                .attr('transform', (d) => `translate(${domain_arc.centroid(d)})`)
                .attr('text-anchor', 'middle')
                .text(function(d) { return d.data.domain; });

        this.domain_score_labels = this.domain_label_group.selectAll('text2')
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append('text')
                .attr('class', 'centeredLabel')
                .style('fill',  function(d){return d.data.score_text_color;})
                .attr('transform', function(d){
                    var centroid = domain_arc.centroid(d);
                    return `translate(${[centroid[0],centroid[1]+15]})`;
                }).attr('text-anchor', 'middle');

        // add detail labels
        this.detail_labels = this.detail_label_group.selectAll('text')
            .data(this.pie_layout(this.question_donut_data))
            .enter().append('text')
            .attr('class', 'centeredLabel')
            .style('fill',  function(d){return d.data.score_text_color;})
            .attr('transform', (d) => `translate(${details_arc.centroid(d)})`)
            .attr('text-anchor', 'middle')
            .text(function(d) { return d.data.score_text; });

        // add detail arcs
        var detail_arcs = this.detail_arc_group.selectAll('path')
                .data(this.pie_layout(this.question_donut_data))
            .enter()
                .append('path')
                .attr('fill', function(v){return v.data.score_color;})
                .attr('class', 'donuts metric_arc')
                .attr('d', details_arc)
                .on('mouseover', function(v1){
                    if (self.viewlock) return;
                    d3.select(this).classed('hovered', true);
                    $(':animated').promise().done(function(){
                        self.show_subset(v1.data);
                    });
                })
                .on('mouseout', function(v){
                    if (self.viewlock) return;
                    d3.select(this).classed('hovered', false);
                    detail_arcs.classed('hovered', false);
                    domain_arcs.classed('hovered', false);
                    self.subset_div.fadeOut('500', function(){self.clear_subset();});
                });
        this.detail_arcs = detail_arcs;

        // add domain arcs
        var domain_arcs = this.domain_arc_group.selectAll('path')
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append('path')
                .attr('class', 'donuts domain_arc')
                .attr('d', domain_arc);
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
        this.title = this.vis.append('svg:text')
            .attr('x', this.w)
            .attr('y', this.h)
            .attr('text-anchor', 'end')
            .attr('class','dr_title')
            .text('{0} risk of bias summary'.printf(this.study.data.short_citation));

        setTimeout(function(){self.toggle_domain_width();}, 2.0);
    }

    toggle_domain_width(){
        var new_radius = this.radius_middle;
        if (this.domain_outer_radius === this.radius_middle)
            new_radius = this.radius_outer;

        this.domain_arc = d3.svg.arc()
            .innerRadius(this.radius_inner)
            .outerRadius(new_radius);
        this.domain_outer_radius = new_radius;

        this.domain_arcs
            .transition()
            .duration('500')
            .attr('d', this.domain_arc);

        var domain_arc = this.domain_arc;
        this.domain_domain_labels
            .transition()
            .duration('500')
	.attr('transform', (d) => `translate(${(domain_arc.centroid(d))}) translate(0,${(d.data.idxOrder)>=(this.study.riskofbias.length)/2?10:-10})`);

        this.domain_score_labels
            .transition()
            .duration('500')
            .attr('transform', function(d){
                var centroid = domain_arc.centroid(d);
                return `translate(${[centroid[0],centroid[1]+15]})`;
            });
    }

    clear_subset(){
        this.subset_div.empty();
    }

    show_subset(metric){
        this.clear_subset();
        this.subset_div.append('<h4>{0} domain</h4>'.printf(metric.parent.domain_text));
        var ol = $('<ol class="score-details"></ol>'),
            div = $('<div>').text(metric.score_text)
                            .attr('class', 'scorebox')
                            .css('background', metric.score_color),
            metric_txt = $('<b>').text(metric.criterion),
            notes_txt = $('<p>').html(metric.notes).css({'height': 250, 'overflow': 'auto'});
        ol.append($('<li>').html([div, metric_txt, notes_txt]));
        this.subset_div.append(ol);
        this.subset_div.fadeIn('500');
    }
}

export default Donut;
