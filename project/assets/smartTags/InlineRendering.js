import $ from '$';

import {
    renderRiskOfBiasDisplay,
} from 'robTable/components/RiskOfBiasDisplay';


class InlineRendering {

    constructor(data){
        this.data = data;
        this.$title = $('<div class="row-fluid inlineSmartTagTitle">');
        this.$div = $('<div class="row-fluid">');
        this.$caption = $('<div class="row-fluid inlineSmartTagCaption">').html(data.$tag.text());
        this.$container = $('<div class="inlineSmartTagContainer container-fluid">')
                            .append([this.$title, this.$div, this.$caption])
                            .data('obj', this);

        this.data.$tag.replaceWith(this.$container);
        return this;
    }

    static reset_renderings($frame){
        $frame = $frame || $(document);
        $frame.find('.inlineSmartTagContainer').each(function(){
            $(this).data('obj').reset_rendering();
        });
    }

    static getInline($node){
        return $node.parents('.inlineSmartTagContainer');
    }

    setTitle($content){
        var isMax = true,
            clickHandler = $.proxy(function(){
                if (isMax){
                    this.$title.find('.icon-minus').removeClass('icon-minus').addClass('icon-plus');
                    this.$div.fadeOut('slow');
                } else {
                    this.$title.find('.icon-plus').removeClass('icon-plus').addClass('icon-minus');
                    this.$div.fadeIn('slow');
                }
                isMax = !isMax;
            }, this),
            toggler = $('<a title="click to toggle visibility" class="toggler btn btn-mini pull-right"></a>')
                .append('<i class="icon-minus"></i>')
                .click(clickHandler);

        this.$title.append($content.append(toggler));
    }

    setMainContent($content){
        this.$div.html($content);
    }

    reset_rendering(){
        this.$container.replaceWith(this.data.$tag);
        return this.data.$tag[0];
    }

    display_endpoint(obj){
        var title  = $('<h4>').html(obj.build_breadcrumbs()),
            plot_div = $('<div style="height:350px; width:350px">'),
            tbl = $(obj.build_endpoint_table($('<table class="table table-condensed table-striped">'))),
            content = $('<div class="row-fluid">')
                .append($('<div class="span8">').append(tbl))
                .append($('<div class="span4">').append(plot_div));

        this.setTitle(title);
        this.setMainContent(content);
        obj.renderPlot(plot_div);
    }

    display_study(obj){
        var title  = $('<h4><b>{0}</b></h4>'.printf(obj.build_breadcrumbs())),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        renderRiskOfBiasDisplay(obj, content[0]);
    }

    display_visual(obj){
        var title = $('<h4>').html(obj.object_hyperlink()),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        obj.displayAsPage(content, {visualOnly: true});
    }

    display_data_pivot(obj){
        var title  = $('<h4>').html(obj.object_hyperlink()),
            content = $('<div>');

        this.setTitle(title);
        this.setMainContent(content);
        obj.build_data_pivot_vis(content);
    }

}

export default InlineRendering;
