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

    build_section() {

    }

    build_box() {

    }

    build_card() {

    }

    build_list() {

    }

    build_arrow() {

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

        // test plot
        // Declare the chart dimensions and margins.
        const width = 640;
        const height = 400;
        const marginTop = 20;
        const marginRight = 20;
        const marginBottom = 30;
        const marginLeft = 40;

        // Declare the x (horizontal position) scale.
        const x = d3.scaleUtc()
            .domain([new Date("2023-01-01"), new Date("2024-01-01")])
            .range([marginLeft, width - marginRight]);

        // Declare the y (vertical position) scale.
        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([height - marginBottom, marginTop]);

        // Create the SVG container.
        this.vis.append("g")
            .attr("width", width)
            .attr("height", height);

        // Add the x-axis.
        this.vis.append("g")
            .attr("transform", `translate(0,${height - marginBottom})`)
            .call(d3.axisBottom(x));

        // Add the y-axis.
        this.vis.append("g")
            .attr("transform", `translate(${marginLeft},0)`)
            .call(d3.axisLeft(y));

    }
}

export default PrismaPlot;
