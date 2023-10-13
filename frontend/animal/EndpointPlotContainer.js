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
            var options = {build_plot_startup: false},
                scatter = new DRPlot(endpoint, this.plot_id, options, this),
                bar = new Barplot(endpoint, this.plot_id, options, this),
                isDichotomous = this.endpoint.isDichotomous();
            this.plot_style = isDichotomous ? [scatter, bar] : [bar, scatter];
            this.toggle_views();
        }
    }

    add_bmd_line(selected_model, line_class) {
        this.plot_style.forEach(plot => {
            if (typeof plot.add_bmd_line == "function") {
                plot.add_bmd_line(selected_model, line_class);
            }
        });
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
                icon: "fa fa-arrow-circle-right",
                on_click() {
                    ep.toggle_views();
                },
            };

        plot.add_menu_button(options);
    }
}

export default EndpointPlotContainer;
