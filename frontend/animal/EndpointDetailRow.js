import h from "shared/utils/helpers";

import $ from "$";

class EndpointDetailRow {
    constructor(endpoint, div, hide_level, options) {
        /*
         * Prints the endpoint as row containing consisting of an EndpointTable and
         * a DRPlot.
         */
        var plot_div_id = h.randomString(),
            table_id = h.randomString(),
            self = this;
        this.options = options || {};
        this.div = $(div);
        this.endpoint = endpoint;
        this.hide_level = hide_level || 0;

        this.div.empty();
        this.div.append('<a class="close" href="#" style="z-index:right;">×</a>');
        this.div.append(`<h4>${endpoint.build_breadcrumbs()}</h4>`);
        this.div.data("pk", endpoint.data.pk);
        this.div.append(
            `<div class="row">
                <div class="col-md-7">
                    <table id="${table_id}" class="table table-sm table-striped"></table>
                </div>
                <div class="col-md-5">
                    <div id="${plot_div_id}" style="max-width:400px;"></div>
                </div>
            </div>`
        );

        this.endpoint.build_endpoint_table($("#" + table_id));
        this.endpoint.renderPlot($("#" + plot_div_id), {showBmd: true});

        $(div + " a.close").on("click", function (e) {
            e.preventDefault();
            self.toggle_view(false);
        });
        this.object_visible = true;
        this.div.fadeIn("fast");
    }

    toggle_view(show) {
        var obj = this.hide_level === 0 ? $(this.div) : this.div.parents().eq(this.hide_level);
        this.object_visible = show;
        return show === true ? obj.fadeIn("fast") : obj.fadeOut("fast");
    }
}

export default EndpointDetailRow;
