var SmartTag = function(tag){
    var self = this;
    this.$tag = $(tag).data('d', this);
    this.type= this.$tag.data('type');
    this.pk = this.$tag.data('pk');
    this.resource = undefined;
    this.rendering = this.$tag.is('span') ? "tooltip" : "inline";
    if (this.rendering === "tooltip"){
        this.$tag.on('click', function(e){self.show_resource(e);});
    } else {
        this._fetch_resource();
    }
};

SmartTag.toggle_disabled = function(e){
    e.preventDefault();
    $('span.smart-tag').toggleClass('active');
};

SmartTag.initialize_tags = function($frame){
    var doc = $frame || $(document);

    doc.find('span.smart-tag')
        .each(function(i, v){ if(!$(this).data('d')){new SmartTag(v);}})
        .addClass('active');

    doc.find('div.smart-tag')
        .each(function(i, v){if(!$(this).data('d')){new SmartTag(v);}});
};

SmartTag.prototype._fetch_resource = function(e){
    var self = this,
        func,
        tooltip_options,
        callback = function(resource){
            self.resource = resource;
            self._render_resource(func, tooltip_options, e);
        };

    switch (this.type){
        case 'endpoint':
            Endpoint.get_object(this.pk, callback);
            func = "display_endpoint";
            tooltip_options = {"width": "500px", "height": "380px"};
            break;
        case 'study':
            Study.get_object(this.pk, callback);
            func = "display_study";
            tooltip_options = {"width": "700px", "height": "450px"};
            break;
        case 'aggregation':
            Aggregation.get_object(this.pk, callback);
            func = "display_aggregation";
            tooltip_options = {"width": "700px", "height": "450px"};
            break;
        case 'data_pivot':
            DataPivot.get_object(this.pk, callback);
            func = "display_data_pivot";
            tooltip_options = {"width": "700px", "height": "450px"};
            break;
        default:
            console.log('Unknown resource type: "{0}"'.printf(this.type));
            return;
    }
};

SmartTag.prototype._render_resource = function(func, tooltip_options, e){
    if (this.rendering === "tooltip"){
        this.tooltip = new PlotTooltip(tooltip_options);
        this.tooltip[func](this.resource, e);
    } else {
        this.inline = new InlineRendering(this);
        this.inline[func](this.resource);
    }
};

SmartTag.prototype.show_resource = function(e){
    if (!this.$tag.hasClass('active')) return;
    if (!this.resource) this._fetch_resource(e);
    if (this.tooltip) this.tooltip.show_tooltip(e);
};

InlineRendering = function(smart_tag){
    this.smart_tag = smart_tag;
    this.$title_div = $('<div></div>');
    this.$div = $('<div class="inline-content"></div>');
    this.$caption = $('<div class="caption">{0}</div>'.printf(smart_tag.$tag.text()));
    this.$container = $('<div class="inline-smart-tag-container row-fluid"></div>')
                        .data('d', this)
                        .append(this.$div, this.$caption);

    $('<div class="span10 offset1 inline-smart-tag"></div>')
        .appendTo(this.$container)
        .append([this.$title_div, this.$div, this.$caption]);

    this.smart_tag.$tag.replaceWith(this.$container);
    return this;
};

InlineRendering.reset_renderings = function($frame){
    var doc = $frame || $(document);
    doc.find('.inline-smart-tag-container').each(function(){
        var rendering = $(this).data('d');
        rendering.$container.replaceWith(rendering.smart_tag.$tag);
    });
};

InlineRendering.prototype._build_title = function($content){
    var self = this,
        toggler = $('<a title="click to toggle visibility" class="toggler btn btn-small pull-right"><i class="icon-minus"></i></a>');
    this.$title_div.append($content.append(toggler));
    this.maximized = true;
    this.$title_div.on('click', '.toggler', function(){
        var v = (self.maximized) ? self.minimize_content() : self.maximize_content();
    });
};

InlineRendering.prototype.minimize_content = function(){
    this.$title_div.find('.icon-minus').removeClass('icon-minus').addClass('icon-plus');
    this.$div.fadeOut("slow");
    this.maximized = false;
};

InlineRendering.prototype.maximize_content = function(){
    this.$title_div.find('.icon-plus').removeClass('icon-plus').addClass('icon-minus');
    this.$div.fadeIn("slow");
    this.maximized = true;
};

InlineRendering.prototype.display_endpoint = function(endpoint){
    var title  = $('<h4><b>{0}</b></h4>'.printf(endpoint.build_breadcrumbs())),
        plot_div = $('<div style="height:350px; width:350px"></div'),
        tbl = $(endpoint.build_endpoint_table($('<table class="table table-condensed table-striped"></table>'))),
        content = [plot_div,
                   tbl];
    this._build_title(title);
    this.$div.html(content);
    new EndpointPlotContainer(endpoint, plot_div);
};

InlineRendering.prototype.display_study = function(study){
    var title  = $('<h4><b>{0}</b></h4>'.printf(study.build_breadcrumbs())),
        content = $('<div></div');
    this.$div.html([content]);
    this._build_title(title);
    new StudyQuality_TblCompressed(study, content, {'show_all_details_startup': false});
};

InlineRendering.prototype.display_aggregation = function(aggregation){
    var title  = $('<h4>{0}</h4>'.printf(aggregation.name)),
        plot_div = $('<div></div>'),
        tbl_div = $('<div></div>'),
        tbl_toggle = $('<a class="btn btn-small" id="table_toggle">Toggle table style <i class="icon-chevron-right"></i></a>'),
        content = [plot_div, tbl_div, tbl_toggle];
    aggregation.build_table(tbl_div);
    this.$div.html(content);
    this._build_title(title);
    aggregation.build_plot(plot_div);
};

InlineRendering.prototype.display_data_pivot = function(data_pivot){
    var title  = $('<h4>{0}</h4>'.printf(data_pivot.title)),
        plot_div = $('<div></div>');

    this.$div.html(plot_div);
    this._build_title(title);
    data_pivot.build_data_pivot_vis(plot_div);
};

InlineRendering.prototype.reset_rendering = function(){
    this.$container.replaceWith(this.smart_tag.$tag);
};
