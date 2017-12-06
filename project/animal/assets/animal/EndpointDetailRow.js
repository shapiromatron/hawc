import $ from '$';

class EndpointDetailRow {
    constructor(endpoint, div, hide_level, options) {
        /*
         * Prints the endpoint as row containing consisting of an EndpointTable and
         * a DRPlot.
         */
        var plot_div_id = String.random_string(),
            table_id = String.random_string(),
            self = this;
        this.options = options || {};
        this.div = $(div);
        this.endpoint = endpoint;
        this.hide_level = hide_level || 0;

        this.div.empty();
        this.div.append(
            '<a class="close" href="#" style="z-index:right;">×</a>'
        );
        this.div.append('<h4>{0}</h4>'.printf(endpoint.build_breadcrumbs()));
        this.div.data('pk', endpoint.data.pk);
        this.div.append(
            '<div class="row-fluid"><div class="span7"><table id="{0}" class="table table-condensed table-striped"></table></div><div class="span5"><div id="{1}" style="max-width:400px;" class="d3_container"></div></div></div>'.printf(
                table_id,
                plot_div_id
            )
        );

        this.endpoint.build_endpoint_table($('#' + table_id));
        this.endpoint.renderPlot($('#' + plot_div_id));

        $(div + ' a.close').on('click', function(e) {
            e.preventDefault();
            self.toggle_view(false);
        });
        this.object_visible = true;
        this.div.fadeIn('fast');
    }

    toggle_view(show) {
        var obj =
            this.hide_level === 0
                ? $(this.div)
                : this.div.parents().eq(this.hide_level);
        this.object_visible = show;
        return show === true ? obj.fadeIn('fast') : obj.fadeOut('fast');
    }
}

export default EndpointDetailRow;
