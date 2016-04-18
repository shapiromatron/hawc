var SmartTag = function(tag){
    var self = this;
    this.$tag = $(tag).data('obj', this);
    this.type = this.$tag.data('type');
    this.pk = this.$tag.data('pk');
    this.resource = undefined;
    this.rendering = this.$tag.is('span') ? "tooltip" : "inline";
    if (this.rendering === "tooltip"){
        this.$tag.on('click', $.proxy(this.display_modal, this));
    } else {
        this.display_inline();
    }
};
_.extend(SmartTag, {
    toggle_disabled: function(e){
        e.preventDefault();
        $('span.smart-tag').toggleClass('active');
    },
    initialize_tags: function($frame){
        var doc = $frame || $(document);

        doc.find('span.smart-tag')
            .each(function(i, v){ if(!$(this).data('obj')){new SmartTag(v);}})
            .addClass('active');

        doc.find('div.smart-tag')
            .each(function(i, v){if(!$(this).data('obj')){new SmartTag(v);}});
    },
    context: {
        "endpoint":     {"Cls": Endpoint,    "inline_func": "display_endpoint"},
        "study":        {"Cls": Study,       "inline_func": "display_study"},
        "visual":       {"Cls": Visual,      "inline_func": "display_visual"},
        "data_pivot":   {"Cls": DataPivot,   "inline_func": "display_data_pivot"},
    },
    getExistingTag: function($node){
        // if the node is an existing Tag; return the $node; else return none.
        var smart_tags = $node.parents('.smart-tag'),
            smart_divs = $node.parents('.inlineSmartTagContainer');

        if(smart_tags.length>0) return smart_tags[0];
        if(smart_divs.length>0){
          // reset inline representation to basic div caption
          var inline = $(smart_divs[0]).data('obj');
          inline.reset_rendering();
          return inline.data.$tag[0];
        }
        return null;
    }
});
_.extend(SmartTag.prototype, {
    display_inline: function(){
        var self = this,
            context = SmartTag.context[this.type],
            cb;

        if (context === undefined){
            console.log('unknown context: {0}'.printf(this.type))
        } else {
            cb = $.proxy(
                function(obj){new InlineRendering(this)[context.inline_func](obj);},
                this);
            context.Cls.get_object(this.pk, cb);
        }
    },
    display_modal: function(e){
        if(!$(e.target).hasClass('active')) return;
        SmartTag.context[this.type].Cls.displayAsModal(this.pk);
    }
});


var SmartTagContainer = function($el, options){
    options = options || {};
    this.$el = $el;

    this.$el.on('SmartTagContainerReady', function(){
        SmartTag.initialize_tags($el)
    });

    if (options.showOnStartup) this.ready();
}
_.extend(SmartTagContainer.prototype, {
    ready: function(){
        this.$el.trigger('SmartTagContainerReady');
    },
    getEl: function(){
        return this.$el;
    }
});


var SmartTagEditor = function($el, options){
    options = options || {};
    this.$el = $el
    this.init();

    if (options.submitEl){
        var self = this;
        $(options.submitEl).submit(function(){
            self.prepareSubmission();
            return true;
        });
    }
}
_.extend(SmartTagEditor.prototype, {
    init: function(){
      this.$el
        .css("height", "300px")
        .wysihtml5({
          "smartTag": true,
          "smartTagModal": "#smartTagModal",
          "font-styles": false,
          "stylesheets": [
            "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.2.2/css/bootstrap.min.css",
            "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.2.2/css/bootstrap-responsive.min.css",
            "/static/css/hawc.css",
            "/static/css/d3.css"
          ]
        });

      var editor = this.$el.data("wysihtml5").editor;
      editor.on("load", function(){
        SmartTag.initialize_tags($(editor.composer.doc));
      });
      this.editor = editor;
    },
    prepareSubmission: function(){
        InlineRendering.reset_renderings($(this.editor.composer.doc))
        this.editor.synchronizer.sync();
    },
    setContent: function(content){
        this.editor.setValue(content);
        SmartTag.initialize_tags($(this.editor.composer.element));
    }
});


InlineRendering = function(data){
    this.data = data;
    this.$title = $('<div class="row-fluid inlineSmartTagTitle">');
    this.$div = $('<div class="row-fluid">');
    this.$caption = $('<div class="row-fluid inlineSmartTagCaption">').html(data.$tag.text());
    this.$container = $('<div class="inlineSmartTagContainer container-fluid">')
                        .append([this.$title, this.$div, this.$caption])
                        .data('obj', this);

    this.data.$tag.replaceWith(this.$container);
    return this;
};
_.extend(InlineRendering, {
    reset_renderings: function($frame){
        $frame = $frame || $(document);
        $frame.find('.inlineSmartTagContainer').each(function(){
            $(this).data('obj').reset_rendering();
        });
    },
    getInline: function($node){
        return $node.parents('.inlineSmartTagContainer');
    }
});
_.extend(InlineRendering.prototype, {
    setTitle: function($content){
        var isMax = true,
            clickHandler = $.proxy(function(){
                if (isMax){
                    this.$title.find('.icon-minus').removeClass('icon-minus').addClass('icon-plus');
                    this.$div.fadeOut("slow");
                } else {
                    this.$title.find('.icon-plus').removeClass('icon-plus').addClass('icon-minus');
                    this.$div.fadeIn("slow");
                }
                isMax = !isMax;
            }, this),
            toggler = $('<a title="click to toggle visibility" class="toggler btn btn-mini pull-right"></a>')
                .append('<i class="icon-minus"></i>')
                .click(clickHandler);

        this.$title.append($content.append(toggler));
    },
    setMainContent: function($content){
        this.$div.html($content);
    },
    reset_rendering: function(){
        this.$container.replaceWith(this.data.$tag);
        return this.data.$tag[0];
    },
    display_endpoint: function(obj){
        var title  = $('<h4>').html(obj.build_breadcrumbs()),
            plot_div = $('<div style="height:350px; width:350px">'),
            tbl = $(obj.build_endpoint_table($('<table class="table table-condensed table-striped">'))),
            content = [plot_div, tbl];

        this.setTitle(title);
        this.setMainContent(content);
        new EndpointPlotContainer(obj, plot_div);
    },
    display_study: function(obj){
        var title  = $('<h4><b>{0}</b></h4>'.printf(obj.build_breadcrumbs())),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        new RiskOfBias_TblCompressed(obj, content, {'show_all_details_startup': false});
    },
    display_visual: function(obj){
        var title = $('<h4>').html(obj.object_hyperlink()),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        obj.displayAsPage(content, {visualOnly: true});
    },
    display_data_pivot: function(obj){
        var title  = $('<h4>').html(obj.object_hyperlink()),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        obj.build_data_pivot_vis(content);
    }
});
