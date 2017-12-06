import $ from '$';
import _ from 'underscore';
import d3 from 'd3';

import HAWCModal from 'utils/HAWCModal';

import RiskOfBiasScore from 'riskofbias/RiskOfBiasScore';
import {
    renderCrossStudyDisplay,
} from 'robTable/components/CrossStudyDisplay';
import {
    renderRiskOfBiasDisplay,
} from 'robTable/components/RiskOfBiasDisplay';

import RoBLegend from './RoBLegend';
import D3Visualization from './D3Visualization';


class RoBHeatmapPlot extends D3Visualization {

    constructor(parent, data, options){
        // heatmap of risk of bias information. Criteria are on the y-axis,
        // and studies are on the x-axis
        super(...arguments);
        this.setDefaults();
        this.modal = new HAWCModal();
    }

    render($div){
        this.plot_div = $div.html('');
        this.processData();
        if(this.dataset.length === 0){
            return this.plot_div.html('<p>Error: no studies with risk of bias selected. Please select at least one study with risk of bias.</p>');
        }
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.add_axes();
        this.draw_visualization();
        this.resize_plot_dimensions();
        this.add_menu();
        this.build_labels();
        this.build_legend();
        this.trigger_resize();
    }

    get_plot_sizes(){
        this.w = this.cell_size*this.xVals.length;
        this.h = this.cell_size*this.yVals.length;
        var menu_spacing = 40;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
            menu_spacing) + 'px'});
    }

    setDefaults(){
        _.extend(this, {
            firstPass: true,
            included_metrics: [],
            padding: {},
            x_axis_settings: {
                scale_type: 'ordinal',
                text_orient: 'top',
                axis_class: 'axis x_axis',
                gridlines: true,
                gridline_class: 'primary_gridlines x_gridlines',
                axis_labels: true,
                label_format: undefined, //default
            },
            y_axis_settings: {
                scale_type: 'ordinal',
                text_orient: 'left',
                axis_class: 'axis y_axis',
                gridlines: true,
                gridline_class: 'primary_gridlines x_gridlines',
                axis_labels: true,
                label_format: undefined, //default
            },
        });
    }

    processData(){

        var dataset = [],
            included_metrics = this.data.settings.included_metrics,
            studies, metrics, xIsStudy;

        _.each(this.data.aggregation.metrics_dataset, function(metric){
            _.chain(metric.rob_scores)
             .filter(function(rob){
                 return _.contains(included_metrics, rob.data.metric.id);
             }).each(function(rob){
                 // Check for short_name setting on the metric
                 var metric_name = rob.data.metric.name;
                 if (rob.data.metric.use_short_name === true && rob.data.metric.short_name !== '') {
                    metric_name = rob.data.metric.short_name;
                 }
                 dataset.push({
                     riskofbias:         rob,
                     study:              rob.study,
                     study_label:        rob.study.data.short_citation,
                     metric:             rob.data.metric,
                     metric_label:       metric_name,
                     score:              rob.data.score,
                     score_text:         rob.data.score_text,
                     score_color:        rob.data.score_color,
                     score_text_color:   rob.data.score_text_color,
                 });
             });
        });

        studies = _.chain(dataset)
                   .map(function(d){return d.study_label;})
                   .uniq()
                   .value();

        metrics = _.chain(dataset)
                   .map(function(d){return d.metric_label;})
                   .uniq()
                   .value();

        if(this.firstPass){
            _.extend(this.padding, {
                top:             this.data.settings.padding_top,
                right:           this.data.settings.padding_right,
                bottom:          this.data.settings.padding_bottom,
                left:            this.data.settings.padding_left,
                top_original:    this.data.settings.padding_top,
                right_original:  this.data.settings.padding_right,
                left_original:   this.data.settings.padding_left,
            });
            this.firstPass = false;
        }

        xIsStudy = (this.data.settings.x_field!=='metric');
        _.extend(this,{
            cell_size: this.data.settings.cell_size,
            dataset,
            studies,
            metrics,
            title_str: this.data.settings.title,
            x_label_text: this.data.settings.xAxisLabel,
            y_label_text: this.data.settings.yAxisLabel,
            xIsStudy,
            xVals: (xIsStudy)  ? studies : metrics,
            yVals: (!xIsStudy) ? studies : metrics,
            xField: (xIsStudy)  ? 'study_label' : 'metric_label',
            yField: (!xIsStudy) ? 'study_label' : 'metric_label',
        });
    }

    add_axes() {
        _.extend(this.x_axis_settings, {
            domain: this.xVals,
            rangeRound: [0, this.w],
            number_ticks: this.xVals.length,
            x_translate: 0,
            y_translate: 0,
        });

        _.extend(this.y_axis_settings, {
            domain: this.yVals,
            rangeRound: [0, this.h],
            number_ticks: this.yVals.length,
            x_translate: 0,
            y_translate: 0,
        });

        this.build_y_axis();
        this.build_x_axis();

        d3.select(this.svg).selectAll('.x_axis text')
            .style('text-anchor', 'start')
            .attr('dx', '5px')
            .attr('dy', '0px')
            .attr('transform', 'rotate(-25)');
    }

    draw_visualization(){
        var self = this,
            x = this.x_scale,
            y = this.y_scale,
            width = this.cell_size,
            half_width = width/2,
            showSQs = function(v){
                self.print_details(self.modal.getBody(), $(this).data('robs'));
                self.modal
                    .addHeader('<h4>Risk of bias details: {0}</h4>'.printf(this.textContent))
                    .addFooter('')
                    .show({maxWidth: 900});
            },
            getMetricSQs = function(i, v){
                var vals = self.dataset.filter(function(e,i,a){return e.metric_label===v.textContent;});
                vals = vals.map(function(v){return v.riskofbias;});
                $(this).data('robs', {type: 'metric', robs: vals});
            },
            getStudySQs = function(i, v){
                var vals = self.dataset.filter(function(e,i,a){return e.study_label===v.textContent;});
                vals = vals.map(function(v){return v.riskofbias;});
                $(this).data('robs', {type: 'study', robs: vals});
            },
            hideHovers = function(v){
                self.draw_hovers(this, {draw: false});
            };

        this.cells_group = this.vis.append('g');

        this.cells = this.cells_group.selectAll('svg.rect')
            .data(this.dataset)
          .enter().append('rect')
            .attr('x', function(d){return x(d[self.xField]);})
            .attr(
                'y'
                ,function(d) {
                    return y(d[self.yField]);
                }
            )
            .attr('height', width)
            .attr('width', width)
            .attr(
                'class',
                function(d) {
                    var returnValue = "heatmap_selectable";

                    if (d.metric.domain.is_overall_confidence) {
                        returnValue = "heatmap_selectable_bold";
                    }

                    return returnValue;
                }
            )
            .style('fill', function(d){return d.score_color;})
        .on('mouseover', function(v,i){self.draw_hovers(v, {draw: true, type: 'cell'});})
        .on('mouseout', function(v,i){self.draw_hovers(v, {draw: false});})
        .on('click', function(v){
            self.print_details(self.modal.getBody(), {type: 'cell', robs: [v]});
            self.modal
                .addHeader('<h4>Risk of bias details</h4>')
                .addFooter('')
                .show({maxWidth: 900});
        });

        this.score = this.cells_group.selectAll('svg.text')
            .data(this.dataset)
            .enter().append('text')
                .attr('x', function(d){return (x(d[self.xField]) + half_width);})
                .attr('y', function(d){return (y(d[self.yField]) + half_width);})
                .attr('text-anchor', 'middle')
                .attr('dy', '3.5px')
                .attr(
                    'class'
                    ,function(d) {
                        var returnValue = "centeredLabel";

                        if (
                            (typeof(d.metric) != "undefined")
                            && (typeof(d.metric.domain) != "undefined")
                            && (typeof(d.metric.domain.is_overall_confidence) === "boolean")
                            && (d.metric.domain.is_overall_confidence)
                        ) {
                            returnValue = "centeredLabel_bold";
                        }

                        return returnValue;
                    }
                )
                .style('fill',  function(d){return d.score_text_color;})
                .text(function(d){return d.score_text;});

        $('.x_axis text').each( (this.xIsStudy) ? getStudySQs : getMetricSQs )
            .attr('class', 'heatmap_selectable')
            .on('mouseover', function(v){self.draw_hovers(this, {draw: true, type: 'column'});})
            .on('mouseout', hideHovers)
            .on('click', showSQs);

        $('.y_axis text').each( (!this.xIsStudy) ? getStudySQs : getMetricSQs )
            .attr(
                'class'
                ,function(d) {
                    var returnValue = "heatmap_selectable";

                    if (
                        (typeof(self.data) != "undefined")
                        && (typeof(self.data.aggregation) != "undefined")
                        && (typeof(self.data.aggregation.metrics_dataset) != "undefined")
                        && (d < self.data.aggregation.metrics_dataset.length)
                        && (typeof(self.data.aggregation.metrics_dataset[d].domain_is_overall_confidence) == "boolean")
                        && (self.data.aggregation.metrics_dataset[d].domain_is_overall_confidence)
                    ) {
                        var returnValue = "heatmap_selectable_bold";
                    }

                    return returnValue;
                }
            )
            .on('mouseover', function(v){self.draw_hovers(this, {draw: true, type: 'row'});})
            .on('mouseout', hideHovers)
            .on('click', showSQs);

        this.hover_group = this.vis.append('g');
    }

    resize_plot_dimensions(){
        // Resize plot based on the dimensions of the labels.
        var ylabel_height = this.vis.select('.x_axis').node().getBoundingClientRect().height,
            ylabel_width = this.vis.select('.x_axis').node().getBoundingClientRect().width,
            xlabel_width = this.vis.select('.y_axis').node().getBoundingClientRect().width;

        if ((this.padding.top < this.padding.top_original + ylabel_height) ||
            (this.padding.left < this.padding.left_original + xlabel_width) ||
            (this.padding.right < ylabel_width - this.w + this.padding.right_original)){

            this.padding.top = this.padding.top_original + ylabel_height;
            this.padding.left = this.padding.left_original + xlabel_width;
            this.padding.right = ylabel_width - this.w + this.padding.right_original;
            this.render(this.plot_div);
        }
    }

    draw_hovers(v, options){
        if (this.hover_study_bar) this.hover_study_bar.remove();
        if (!options.draw) return;

        var draw_type;
        switch (options.type){
        case 'cell':
            draw_type = {
                x: this.x_scale(v[this.xField]),
                y: this.y_scale(v[this.yField]),
                height: this.cell_size,
                width: this.cell_size};
            break;
        case 'row':
            draw_type = {
                x: 0,
                y: this.y_scale(v.textContent),
                height: this.cell_size,
                width: this.w};
            break;
        case 'column':
            draw_type = {
                x: this.x_scale(v.textContent),
                y: 0,
                height: this.h,
                width: this.cell_size};
            break;
        }

        this.hover_study_bar = this.hover_group.selectAll('svg.rect')
            .data([draw_type])
            .enter().append('rect')
                .attr('x', function(d){return d.x;})
                .attr('y', function(d){return d.y;})
                .attr('height', function(d){return d.height;})
                .attr('width', function(d){return d.width;})
                .attr('class', 'heatmap_hovered');
    }

    build_labels(){

        var svg = d3.select(this.svg),
            visMidX = parseInt(this.svg.getBoundingClientRect().width/2, 10),
            visMidY = parseInt(this.svg.getBoundingClientRect().height/2, 10),
            midX = d3.mean(this.x_scale.range()),
            midY = d3.mean(this.y_scale.range());

        if($(this.svg).find('.figureTitle').length === 0){
            svg.append('svg:text')
                .attr('x', visMidX)
                .attr('y', 25)
                .text(this.title_str)
                .attr('text-anchor', 'middle')
                .attr('class','dr_title figureTitle');
        }

        var xLoc = this.padding.left + midX+20,
            yLoc = visMidY*2-5;

        svg.append('svg:text')
            .attr('x', xLoc)
            .attr('y', yLoc)
            .text(this.x_label_text)
            .attr('text-anchor', 'middle')
            .attr('class','dr_axis_labels x_axis_label');

        yLoc = this.padding.top + midY;

        svg.append('svg:text')
            .attr('x', 15)
            .attr('y', yLoc)
            .attr('transform','rotate(270, {0}, {1})'.printf(15, yLoc))
            .text(this.y_label_text)
            .attr('text-anchor', 'middle')
            .attr('class','dr_axis_labels y_axis_label');
    }

    build_legend(){
        if (this.legend || !this.data.settings.show_legend) return;
        let options = {
            dev: this.options.dev || false,
            collapseNR: false,
        };
        this.legend = new RoBLegend(
            this.svg,
            this.data.settings,
            options
        );
    }

    print_details($div, d){
        var config = {
            display: 'all',
            isForm: false,
        };
        // delay rendering until modal is displayed, as component depends on accurate width.
        window.setTimeout(function(){
            switch (d.type){
            case 'cell':
                _.extend(config, {
                    show_study: true,
                    study: {
                        name: d.robs[0].study_label,
                        url:d.robs[0].study.data.url,
                    },
                });
                renderRiskOfBiasDisplay(
                    RiskOfBiasScore.format_for_react([d.robs[0].riskofbias], config),
                    $div[0]);
                break;
            case 'study':
                renderRiskOfBiasDisplay(
                    RiskOfBiasScore.format_for_react(d.robs, config),
                    $div[0]);
                break;
            case 'metric':
                renderCrossStudyDisplay(
                    RiskOfBiasScore.format_for_react(d.robs, config),
                    $div[0]);
                break;
            }
        }, 200);
    }
}

export default RoBHeatmapPlot;
