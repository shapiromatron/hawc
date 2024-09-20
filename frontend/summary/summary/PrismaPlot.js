import HAWCModal from "shared/utils/HAWCModal";
import * as d3 from "d3";


class PrismaPlot {
    constructor(store, options) {
        this.modal = new HAWCModal();
        this.store = store;
        this.options = options;
    }

    render(div) {
        this.plot_div = $(div);
        this.build_plot();
    }

    build_plot() {
        this.plot_div.empty();
        this.svg = d3.select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "A prisma diagram.")
            .attr("class", "d3")
            .node();
        this.vis = d3.select(this.svg).append("g");

    }
}

export default PrismaPlot;
