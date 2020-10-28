import $ from "$";

import Barplot from "./Barplot";
import DRPlot from "./DRPlot";

class EndpointPlotContainer {
    constructor(endpoint, plot_id) {
        //container used for endpoint plot organization
        this.endpoint = endpoint;
        this.plot_div = $(plot_id);
        this.plot_id = plot_id;

        if (!this.endpoint.hasEGdata()) {
            this.plot_div.html("<p>Plot unavailable.</p>");
        } else {
            var options = {build_plot_startup: false};
            this.plot_style = [
                new Barplot(endpoint, this.plot_id, options, this),
                new DRPlot(endpoint, this.plot_id, options, this),
            ];
            this.toggle_views();
        }
    }

    add_bmd_line(selected_model, line_class) {
        if (this.plot.add_bmd_line) {
            this.plot.add_bmd_line(selected_model, line_class);
        }
    }

    toggle_views() {
        // change the current plot style
        if (this.plot) {
            this.plot.cleanup_before_change();
        }
        this.plot_style.unshift(this.plot_style.pop());
        this.plot = this.plot_style[0];
        this.plot.build_plot();
    }

    add_toggle_button(plot) {
        // add toggle to menu options to view other ways
        var ep = this,
            options = {
                id: "plot_toggle",
                cls: "btn btn-sm",
                title: "View alternate visualizations",
                text: "",
                icon: "icon-circle-arrow-right",
                on_click() {
                    ep.toggle_views();
                },
            };

        plot.add_menu_button(options);
    }
}

export default EndpointPlotContainer;
