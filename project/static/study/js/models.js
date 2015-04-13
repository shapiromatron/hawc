var StudyVersion = function(obj, version){
    // implements requirements for js/hawc_utils Version interface
    // unpack JSON object into Study
    for (var i in obj) {
        this[i] = obj[i];
    }
    this.version = version;
    // convert datetime formats
    this.updated = new Date(this.updated);
    this.banner = this.version + ': ' + this.updated + ' by ' + this.changed_by;
};
_.extend(StudyVersion, {
    field_order: ['short_citation', 'citation', 'hero_id', 'summary', 'updated']
});


var Study = function(data){
    this.data = data;
    this.study_quality = [];
    if(this.data.qualities) this.unpack_study_quality();
};
_.extend(Study, {
    get_object: function(id, cb){
        $.get('/study/{0}/json/'.printf(id), function(d){
            cb(new Study(d));
        });
    },
    displayAsModal: function(id){
        Study.get_object(id, function(d){d.displayAsModal();});
    }
});
Study.prototype = {
    has_study_quality: function(){
        return this.study_quality.length>0;
    },
    unpack_study_quality: function(){
        // unpack study-quality information and nest by domain
        var self = this,
            study_quality = [],
            gradient_colors = d3.scale.linear()
                .domain([0, 1, 2, 3, 4])
                .range(SQColors);
        this.data.qualities.forEach(function(v, i){
            v.score_color = gradient_colors(v.score);
            v.score_text_color = String.contrasting_color(v.score_color);
            v.score_text = StudyQuality.score_text[v.score];
            study_quality.push(new StudyQuality(self, v));
        });

        //construct dataset in structure for a donut plot
        this.study_quality = d3.nest()
                                .key(function(d){return d.data.metric.domain.name;})
                                .entries(study_quality);

        // now generate a score for each
        this.study_quality.forEach(function(v, i){
            v.domain = v.values[0].data.metric.domain.id;
            v.domain_text = v.values[0].data.metric.domain.name;
            delete v.key;
            v.criteria = v.values;
            delete v.values;
            // we only want to calculate score for cases where answer !== N/A, or >0
            var non_zeros = d3.sum(v.criteria.map(function(v){return (v.data.score>0)?1:0;}));
            if (non_zeros>0){
                v.score = d3.round(d3.sum(v.criteria, function(v,i){return v.data.score;})/non_zeros,2);
            } else {
                v.score = 0;
            }
            v.score_text = (v.score>0) ? v.score : 'N/A';
            v.score_color = gradient_colors(v.score);
            v.score_text_color = String.contrasting_color(v.score_color);
        });

        // try to put the "other" domain at the end
        var l = this.study_quality.length;
        for(var i=0; i<l; i++){
            if (this.study_quality[i].domain_text.toLowerCase() === "other"){
                this.study_quality.push(this.study_quality.splice(i, 1)[0]);
                break;
            }
        }

        delete this.data.qualities;
    },
    build_breadcrumbs: function(){
        var urls = [{ url: this.data.url, name: this.data.short_citation }];
        return HAWCUtils.build_breadcrumbs(urls);
    },
    get_name: function(){
        return this.data.short_citation;
    },
    build_details_table: function(div){
        var tbl = new DescriptiveTable(),
            links = this._get_identifiers_hyperlinks_ul();
        tbl.add_tbody_tr("Study type", this.data.study_type);
        tbl.add_tbody_tr("Full citation", this.data.full_citation);
        tbl.add_tbody_tr("Abstract", this.data.abstract);
        if (links.children().length>0) tbl.add_tbody_tr("Reference hyperlink", links);
        tbl.add_tbody_tr_list("Literature review tags", this.data.tags.map(function(d){return d.name;}));
        tbl.add_tbody_tr("COI reported", this.data.coi_reported);
        tbl.add_tbody_tr("COI details", this.data.coi_details);
        tbl.add_tbody_tr("Funding source", this.data.funding_source);
        tbl.add_tbody_tr("Study identifier", this.data.study_identifier);
        tbl.add_tbody_tr("Author contacted?", HAWCUtils.booleanCheckbox(this.data.contact_author));
        tbl.add_tbody_tr("Author contact details", this.data.ask_author);
        tbl.add_tbody_tr("Summary text", this.data.summary);
        $(div).html(tbl.get_tbl());
    },
    _get_identifiers_hyperlinks_ul: function(){
        var ul = $('<ul>');

        this.data.identifiers.forEach(function(v){
            if (v.url){
                ul.append($('<li>').append(
                    $('<a>').attr('href', v.url).attr('target', '_blank').text(v.database)));
            }
        });

        return ul;
    },
    add_attachments_row: function(div, attachments){
        if (attachments.length===0) return;

        var tbody = div.find("table tbody"),
            ul = $('<ul>'),
            tr = $('<tr>').append('<th>Attachments</th>'),
            td = $('<td>');

        attachments.forEach(function(v){
            ul.append('<li><a target="_blank" href="{0}">{1}</a> <a class="pull-right" title="Delete {1}" href="{2}"><i class="icon-trash"></i></a></li>'.printf(v.url, v.filename, v.url_delete));
        });
        tbody.append(tr.append(td.append(ul)));
    },
    displayAsModal: function(){
        var self = this,
            modal = new HAWCModal(),
            title = '<h4>{0}</h4>'.printf(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        this.build_details_table($details);
        if(this.has_study_quality()){
            var $sq = $('<div class="span12">')
            $content.prepend($('<div class="row-fluid">').append($sq));
            modal.getModal().on('shown', function(){
                new StudyQuality_TblCompressed(self,
                        $sq,
                        {'show_all_details_startup': false}
                );
            });
        }

        modal.addHeader(title)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 1000});
    }
};


var StudyQuality = function(study, data){
    this.study = study;
    this.data = data;
    this.data.metric.created = new Date(this.data.metric.created);
    this.data.metric.last_updated = new Date(this.data.metric.last_updated);
};
_.extend(StudyQuality, {
    score_text: {0: 'N/A', 1: '--', 2: '-', 3: '+', 4: '++'},
    display_details_divs: function($div, content){
        // insert content into selected div and then draw all animations
        // associated with this insertion.
        $(":animated").promise().done(function() {
            $div.html(content);
            $div.fadeIn();
        }, function(){
            $('.sq_score_bar').each(function(){
                $(this).data('animate')();
            });
        });
    },
    build_study_comparison_div: function(sqs){
        // construct a div which compares one metric across multiple studies.
        // This expects an array of study-quality objects where each object is
        // a different study but ALL objects are the same metric.
        var content = ['<hr><h3>{0}</h3>'.printf(sqs[0].data.metric.domain.name),
                       '<h4>{0}</h4>'.printf(sqs[0].data.metric.metric),
                       '<div class="help-block">{0}</div>'.printf(sqs[0].data.metric.description)];
        sqs.forEach(function(sq){
            content.push('<h4><a target="_blank" href="{0}">{1}</a></h4>'.printf(sq.study.data.url, sq.study.data.short_citation),
                         sq._build_details_div());
        });
        return $('<div class="row-fluid"></div>').html(content);
    },
    build_metric_comparison_div: function(sqs){
        // construct a div which compares one study across multiple metrics.
        // This expects an array of study-quality objects where each object is
        // a different metric but ALL objects are the same study.
        var domain_text,
            content = [];
        sqs.forEach(function(sq){
            if(sq.data.metric.domain.name !== domain_text){
                content.push('<hr><h3>{0}</h3>'.printf(sq.data.metric.domain.name));
                domain_text = sq.data.metric.domain.name;
            }
            content.push('<h4>{0}</h4>'.printf(sq.data.metric.metric),
                         '<div class="help-block">{0}</div>'.printf(sq.data.metric.description),
                         sq._build_details_div());
        });
        return $('<div class="row-fluid"></div>').html(content);
    }
});
StudyQuality.prototype = {
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
            sq_score_bar = $('<div class="sq_score_bar" style="width:15%; background-color:{0};"><span style="padding-right:5px">{1}</span></div>'.printf(this.data.score_color, this.data.score_text))
                .data('animate', function(){
                    $(sq_score_bar).animate({'width': bar_width + '%'}, 500);});
        score_div.append([sq_score_bar, '<p>{0}</p>'.printf(this.data.score_description)]);
        return $div;
    }
};


var StudyQuality_Donut = function(study, plot_id, options){
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.study = study;
    this.plot_div = $(plot_id);
    this.options = options;
    this.viewlock = false;
    if(!this.study.study_quality || this.study.study_quality.length === 0 ) return;
    this.set_defaults(options);
    if(this.options && this.options.build_plot_startup){this.build_plot();}
    $('body').on('keydown', function() {
        if (event.ctrlKey || event.metaKey){self.toggle_lock_view();}
    });
};
_.extend(StudyQuality_Donut.prototype, D3Plot.prototype, {
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

        this.study.study_quality.forEach(function(v1){
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
                .attr("class", "uf_label domain_arc")
                .attr("transform", function(d) { return "translate(" + (domain_arc.centroid(d)) + ")"; })
                .attr("text-anchor", "middle")
                .text(function(d) { return d.data.domain; });

        this.domain_score_labels = this.domain_label_group.selectAll("text2")
                .data(this.pie_layout(this.domain_donut_data))
            .enter()
                .append("text")
                .attr("class", "uf_label")
                .style("fill",  function(d){return d.data.score_text_color;})
                .attr("transform", function(d){
                    var centroid = domain_arc.centroid(d);
                    return "translate(" + [centroid[0],centroid[1]+15] + ")";})
                .attr("text-anchor", "middle");

        // add detail labels
        this.detail_labels = this.detail_label_group.selectAll("text")
            .data(this.pie_layout(this.question_donut_data))
            .enter().append("text")
            .attr("class", "uf_label")
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


var StudyQuality_TblCompressed = function(study, div, options){
    this.study = study;
    this.$div = $(div);
    this.build_table();

    if(options && options.show_all_details_startup){
        this.show_details_div();
    }
};
StudyQuality_TblCompressed.prototype = {
    build_table: function(){
        var self = this;
        this.tbl = $('<table class="table table-condensed"></table>');
        this.build_tbody();
        this.build_footer();
        this.selected_div = $('<div style="display:none"></div>');
        this.$div.html([this.tbl, this.selected_div]);
        $(".tooltips").tooltip();
        $('.sq_criteria').on('click', 'td', function(){self.show_details_div(this);});
        $('.sq_domains').on('click', 'td', function(){self.show_details_div(this);});
    },
    show_details_div: function(selected){
        var $sel = $(selected),
            divs = [],
            self = this,
            show_all_text = 'Show all details';

        this.selected_div.fadeOut();

        if ($sel.data('sqs')){
            divs.push(StudyQuality.build_metric_comparison_div($sel.data('sqs').criteria));
        } else if ($sel.data('sq')) {
            divs.push($sel.data('sq').build_details_div());
        } else {
            // show all details
            selected = this.study;
            this.study.study_quality.forEach(function(v1, i1){
                divs.push(StudyQuality.build_metric_comparison_div(v1.criteria));
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
            StudyQuality.display_details_divs(self.selected_div, divs);
        }
    },
    build_tbody: function(){
        var tbody = $('<tbody></tbody>'),
            tr1 = $('<tr class="sq_domains"></tr>'),
            tr2 = $('<tr class="sq_criteria"></tr>');
        this.study.study_quality.forEach(function(v1, i1){
            v1.criteria.forEach(function(v2, i2){
                if(i2 === 0){
                    tr1.append($('<td class="scorecell domain_cell" colspan="{0}">{1}</td>'.printf(
                                 v1.criteria.length,
                                 v1.domain_text)).data('sqs', v1));
                }
                tr2.append($('<td class="scorecell" style="background-color: {0};"><span class="tooltips" data-toggle="tooltip" title="{1}">{2}</span></td>'.printf(
                                v2.data.score_color,
                                v2.data.metric.metric,
                                v2.data.score_text)).data('sq', v2));
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
};


var StudyQualityAggregation = function(studies){
    this.studies = studies;
    this.metrics_dataset = this.build_metrics_dataset();
};
StudyQualityAggregation.prototype = {
    build_metrics_dataset: function(){
        var arr = [];
        this.studies.forEach(function(study){
            study.study_quality.forEach(function(domain){
                domain.criteria.forEach(function(sq){
                    arr.push(sq);
                });
            });
        });

        var ds = d3.nest()
                    .key(function(d){return d.data.metric.id;})
                    .entries(arr);

        var score_binning = function(d){
            var score_bins = {'0': {study_qualities:[], score:0, score_text:'N/A', score_description: 'Not applicable'},
                              '1': {study_qualities:[], score:1, score_text:'--', score_description: 'Definitely high risk of bias'},
                              '2': {study_qualities:[], score:2, score_text:'-', score_description: 'Probably high risk of bias'},
                              '3': {study_qualities:[], score:3, score_text:'+', score_description: 'Probably low risk of bias'},
                              '4': {study_qualities:[], score:4, score_text:'++', score_description: 'Definitely low risk of bias'}};
            d.study_qualities.forEach(function(sq){
                score_bins[sq.data.score].study_qualities.push(sq);
            });
            return score_bins;
        };

        ds.forEach(function(v){
            v.rename_property('key', 'domain');
            v.rename_property('values', 'study_qualities');
            v.domain_text = v.study_qualities[0].data.metric.domain.name;
            var possible_score = d3.sum(v.study_qualities.map(function(v){return (v.data.score>0)?4:0;})),
                score = d3.sum(v.study_qualities.map(function(v){return v.data.score;}));
            v.score = (possible_score>0)?d3.round(score/possible_score*100, 2):0;
            v.score_bins = score_binning(v);
        });
        return ds;
    }
};


var StudyQualityAggregation_Heatmap = function(sq_agg, plot_div, options){
    // heatmap of study-quality information. Criteria are on the y-axis,
    // and studies are on the x-axis
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.options = options;
    this.set_defaults();
    this.plot_div = $(plot_div);
    this.sq_agg = sq_agg; // expected array
    this.modal = new HAWCModal();
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(StudyQualityAggregation_Heatmap.prototype, D3Plot.prototype, {
    build_plot: function(){
        this.plot_div.html('');
        this.get_dataset();
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.add_axes();
        this.draw_visualizations();
        this.add_final_rectangle();
        this.add_menu();
        this.resize_plot_dimensions();
        this.trigger_resize();
    },
    resize_plot_dimensions: function(){
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
            this.build_plot();
        }
    },
    get_plot_sizes: function(){
        this.w = this.cell_px*this.studies.length;
        this.h = this.cell_px*this.metrics.length;
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
            menu_spacing) + 'px'});
    },
    set_defaults: function(){
        this.padding = {top:10, right:10, bottom:10, left:10};
        this.padding.left_original = this.padding.left;
        this.padding.top_original = this.padding.top;
        this.padding.right_original = this.padding.right;
        this.cell_px = 40;
        this.x_axis_settings = {
            scale_type: 'ordinal',
            text_orient: "top",
            axis_class: 'axis x_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            axis_labels: true,
            label_format: undefined //default
        };

        this.y_axis_settings = {
            scale_type: 'ordinal',
            text_orient: 'left',
            axis_class: 'axis y_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            axis_labels: true,
            label_format: undefined //default
        };
    },
    get_dataset: function(){

        var dataset = [];
        this.sq_agg.metrics_dataset.forEach(function(metric, metric_i){
            metric.study_qualities.forEach(function(sq, sq_i){
                dataset.push({
                    study_quality: sq,
                    study: sq.study,
                    study_label: sq.study.data.short_citation,
                    metric: sq.data.metric,
                    metric_label: sq.data.metric.metric,
                    score: sq.data.score,
                    score_text: sq.data.score_text,
                    score_color: sq.data.score_color,
                    score_text_color: sq.data.score_text_color
                });
            });
        });

        var studies = dataset.map(function(obj) { return obj.study_label; });
        this.studies = studies.filter(function(v,i) { return studies.indexOf(v) == i; });

        var metrics = dataset.map(function(obj) { return obj.metric_label; });
        this.metrics = metrics.filter(function(v,i) { return metrics.indexOf(v) == i; });

        this.dataset = dataset;
        this.title_str = "Title";
        this.x_label_text = "Studies";
        this.y_label_text = "Criteria";
    },
    add_axes: function() {
        $.extend(this.x_axis_settings, {
            domain: this.studies,
            rangeRound: [0, this.w],
            number_ticks: this.studies.length,
            x_translate: 0,
            y_translate: 0
        });

        $.extend(this.y_axis_settings, {
            domain: this.metrics,
            number_ticks: this.metrics.length,
            rangeRound: [0, this.h],
            x_translate: 0,
            y_translate: 0
        });

        this.build_y_axis();
        this.build_x_axis();

        d3.selectAll('.x_axis text')
            .style("text-anchor", "start")
            .attr("dx", "5px")
            .attr("dy", "0px")
            .attr("transform", "rotate(-25)");
    },
    draw_visualizations: function(){
        var x = this.x_scale,
            y = this.y_scale,
            width = this.cell_px,
            half_width = width/2,
            self = this;

        this.cells_group = this.vis.append("g");

        this.cells = this.cells_group.selectAll("svg.rect")
            .data(this.dataset)
          .enter().append("rect")
            .attr("x", function(d){return x(d.study_label);})
            .attr("y", function(d){return y(d.metric_label);})
            .attr("height", width)
            .attr("width", width)
            .attr("class", "heatmap_selectable")
            .style('fill', function(d){return d.score_color;})
        .on('mouseover', function(v,i){self.draw_hovers(v, {draw: true, type: 'cell'});})
        .on('mouseout', function(v,i){self.draw_hovers(v, {draw: false});})
        .on('click', function(v){
            self.print_details(self.modal.getBody(), {type: 'cell', sqs: [v]})
            self.modal
                .addHeader('<h4>Study Quality Details</h4>')
                .addFooter("")
                .show({maxWidth: 900});
        });
        this.score = this.cells_group.selectAll("svg.text")
            .data(this.dataset)
            .enter().append("text")
                .attr("x", function(d){return (x(d.study_label) + half_width);})
                .attr("y", function(d){return (y(d.metric_label) + half_width);})
                .attr("text-anchor", "middle")
                .attr("dy", "3.5px")
                .attr("class", "uf_label")
                .style("fill",  function(d){return d.score_text_color;})
                .text(function(d){return d.score_text;});

        $('.y_axis text').each(function(i, v){
                var vals = self.dataset.filter(function(e,i,a){return e.metric_label===v.textContent;});
                vals = vals.map(function(v){return v.study_quality;});
                $(this).data('sqs', {type: 'metric', sqs: vals});
            }).on('mouseover', function(v){self.draw_hovers(this, {draw: true, type: 'row'});})
            .attr('class', 'heatmap_selectable')
            .on('mouseout', function(v){self.draw_hovers(this, {draw: false});})
            .on('click', function(v){
                self.print_details(self.modal.getBody(), $(this).data('sqs'))
                self.modal
                    .addHeader('<h4>Study Quality Details</h4>')
                    .addFooter("")
                    .show({maxWidth: 900});
            });

        $('.x_axis text').each(function(i, v){
                var vals = self.dataset.filter(function(e,i,a){return e.study_label===v.textContent;});
                vals = vals.map(function(v){return v.study_quality;});
                $(this).data('sqs', {type: 'study', sqs: vals});
            }).attr('class', 'heatmap_selectable')
            .on('mouseover', function(v){self.draw_hovers(this, {draw: true, type: 'column'});})
            .on('mouseout', function(v){self.draw_hovers(this, {draw: false});})
            .on('click', function(v){
                self.print_details(self.modal.getBody(), $(this).data('sqs'))
                self.modal
                    .addHeader('<h4>Study Quality Details</h4>')
                    .addFooter("")
                    .show({maxWidth: 900});
            });

        this.hover_group = this.vis.append("g");
    },
    _modal_sizing: function(){
        $('#sq_details_modal').css({'width': ($(window).width()-100),
                                    'height': ($(window).height()-100),
                                    'top': '50px',
                                    'left': '50px',
                                    'margin': '0px'
                                    });
        $('#sq_details_modal .modal-body').css({'max-height': ($(window).height()-185)});
    },
    draw_hovers: function(v, options){
        if (this.hover_study_bar) this.hover_study_bar.remove();
        if (options.draw){
            var draw_type;
            switch (options.type){
                case 'cell':
                    draw_type = {
                        x: this.x_scale(v.study_label),
                        y: this.y_scale(v.metric_label),
                        height: this.cell_px,
                        width: this.cell_px};
                    break;
                case 'row':
                    draw_type = {
                        x: 0,
                        y: this.y_scale(v.textContent),
                        height: this.cell_px,
                        width: this.w};
                    break;
                case 'column':
                    draw_type = {
                        x: this.x_scale(v.textContent),
                        y: 0,
                        height: this.h,
                        width: this.cell_px};
                    break;
            }

            this.hover_study_bar = this.hover_group.selectAll("svg.rect")
                .data([draw_type])
                .enter().append("rect")
                    .attr("x", function(d){return d.x;})
                    .attr("y", function(d){return d.y;})
                    .attr("height", function(d){return d.height;})
                    .attr("width", function(d){return d.width;})
                    .attr('class', 'heatmap_hovered');
        }
    },
    print_details: function($div, d){
        var content = [];

        switch (d.type){
            case 'cell':
                content.push(d.sqs[0].study_quality.build_details_div({show_study: true}));
                break;
            case 'study':
                content.push(StudyQuality.build_metric_comparison_div(d.sqs));
                break;
            case 'metric':
                content.push(StudyQuality.build_study_comparison_div(d.sqs));
                break;
        }

        StudyQuality.display_details_divs($div, content);
    }
});


var StudyQualityAggregation_Stacked = function(sq_agg, plot_div, options){
    // stacked-bars of study-quality information. Criteria are on the y-axis,
    // and studies are on the x-axis
    var self = this;
    D3Plot.call(this); // call parent constructor
    this.options = options;
    this.set_defaults();
    this.plot_div = $(plot_div);
    this.sq_agg = sq_agg; // expected array
    if(this.options.build_plot_startup){this.build_plot();}
};
_.extend(StudyQualityAggregation_Stacked.prototype, D3Plot.prototype, {
    build_plot: function(){
        this.plot_div.html('');
        this.get_dataset();
        this.get_plot_sizes();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.build_x_label();
        this.draw_visualizations();
        this.add_final_rectangle();
        this.add_menu();
        this.resize_plot_dimensions();
        this.trigger_resize();
    },
    resize_plot_dimensions: function(){
        // Resize plot based on the dimensions of the labels.
        var xlabel_width = this.vis.select('.y_axis').node().getBoundingClientRect().width;
        if (this.padding.left < this.padding.left_original + xlabel_width) {
            this.padding.left = this.padding.left_original + xlabel_width;
            this.build_plot();
        }
    },
    get_plot_sizes: function(){
        this.h = this.cell_px*this.metrics.length;
        var menu_spacing = (this.options.show_menu_bar) ? 40 : 0;
        this.plot_div.css({'height': (this.h + this.padding.top + this.padding.bottom +
            menu_spacing) + 'px'});
    },
    set_defaults: function(){
        this.padding = {top:10, right:20, bottom:35, left:5};
        this.padding.left_original = this.padding.left;
        this.padding.top_original = this.padding.top;
        this.padding.right_original = this.padding.right;
        this.w = 400;
        this.cell_px = 30;
        this.x_axis_settings = {
            domain: [0, 1],
            scale_type: "linear",
            text_orient: "bottom",
            axis_class: "axis x_axis",
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            axis_labels: true,
            label_format: d3.format(".0%")
        };

        this.y_axis_settings = {
            scale_type: 'ordinal',
            text_orient: 'left',
            axis_class: 'axis y_axis',
            gridlines: true,
            gridline_class: 'primary_gridlines x_gridlines',
            axis_labels: true,
            label_format: undefined //default
        };
        this.color_scale = d3.scale.ordinal().range(SQColors);
        this.x_label_text = "Fraction of studies evaluated";
    },
    get_dataset: function(){

        var dataset = [];
        this.sq_agg.metrics_dataset.forEach(function(metric, idx){
            var vals = {"metric_label": metric.study_qualities[0].data.metric.metric,
                        "N/A":0, "--":0, "-":0, "+":0, "++":0},
                weight = 1/metric.study_qualities.length;
            metric.study_qualities.forEach(function(sq){
                vals[sq.data.score_text] += weight;
            });
            dataset.push(vals);
        });

        var metrics = dataset.map(function(obj) { return obj.metric_label; });
        this.metrics = metrics.filter(function(v,i) { return metrics.indexOf(v) == i; });

        this.stack_order = ["N/A", "--", "-", "+", "++"];
        this.stack = d3.layout.stack()(this.stack_order.map(function(score){
            return dataset.map(function(d){
                return {x: d.metric_label, y: d[score]};
            });
        }));
    },
    add_axes: function(){
        $.extend(this.x_axis_settings, {
            rangeRound: [0, this.w],
            number_ticks: 5,
            x_translate: 0,
            y_translate: this.h
        });

        $.extend(this.y_axis_settings, {
            domain: this.metrics,
            number_ticks: this.metrics.length,
            rangeRound: [0, this.h],
            x_translate: 0,
            y_translate: 0
        });

        this.build_y_axis();
        this.build_x_axis();
    },
    draw_visualizations: function(){
        var plot = this,
            x = this.x_scale,
            y = this.y_scale,
            colors = this.color_scale;

        this.bar_group = this.vis.append("g");

        // Add a group for each score.
        var groups = this.vis.selectAll("g.score")
              .data(this.stack)
            .enter().append("svg:g")
              .attr("class", "score")
              .style("fill", function(d, i){return colors(i);})
              .style("stroke", function(d, i){return d3.rgb(colors(i)).darker();});

        // Add a rect for each date.
        var rects = groups.selectAll("rect")
              .data(Object)
            .enter().append("svg:rect")
              .attr("x", function(d) { return x(d.y0); })
              .attr("y", function(d) { return y(d.x)+5; })
              .attr("width", function(d) { return x(d.y); })
              .attr("height", 20)
              .on('mouseover', function(d){
                    plot.show_tooltip(d.x, (d.y*100 + '%'));
                })
                .on('mouseout', function(){
                    plot.hide_tooltip();
                });

        // var texts = groups.selectAll("text")
        //       .data(Object)
        //     .enter().append("text")
        //     .attr("class", "uf_label")
        //     .attr("x", function(d){return (x(d.y0) + x(d.y)/2);})
        //     .attr("y", function(d){return (y(d.x)+20);})
        //     .attr("text-anchor", "middle")
        //     .style("fill", "#555")
        //     .style("opacity", 1)
        //     .text(function(d){return (d.y>0) ? (d.y*100 + '%') : "";});
    }
});
