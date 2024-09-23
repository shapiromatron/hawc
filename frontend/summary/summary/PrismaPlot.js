import * as d3 from "d3";
import HAWCModal from "shared/utils/HAWCModal";

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

    build_section(obj) {
        const g = this.vis.append("g");
        const rect = g.append("rect")
            .attr("x", obj.rx)
            .attr("y", obj.ry)
            .attr("width", obj.width)
            .attr("height", obj.height)
            .style("fill", obj.bg_color)
            .style("border-width", obj.border_width)
            .attr("stroke", obj.border_color);
        const titleBox = rect.append("rect")
            .attr("width", obj.width/2)
            .attr("height", obj.height/2)
            .attr("fill", obj.bg_color)
            .style("border-width", obj.border_width)
            .attr("stroke", obj.border_color);
        titleBox.append("text")
            .text(obj.name)
            .attr("class", "prisma_section_text")
            .style("font-color", obj.font_color);
    }

    apply_text_style(obj, style) {
        // check style string for options like bold and left justified
    }

    build_box(obj, parent) {}

    build_card(obj) {}

    build_list(obj) {}

    build_arrow(obj) {}

    build_plot() {
        // test data
        this.dataset = {
            title: "Prisma Visual",
            sections: [
                {
                    key: "section1key",
                    name: "Section 1",
                    width: 200,
                    height: 100,
                    border_width: 2,
                    rx: 50,
                    ry: 10,
                    bg_color: "yellow",
                    border_color: "Black",
                    font_color: "Black",
                    text_style: "Left justified",
                },
                {
                    key: "section2key",
                    name: "Section 2",
                    width: 200,
                    height: 100,
                    border_width: 2,
                    rx: 50,
                    ry: 300,
                    bg_color: "white",
                    border_color: "Black",
                    font_color: "Black",
                    text_style: "Bold",
                },
            ],
            boxes: [],
            bulleted_lists: [],
            cards: [],
            arrows: [],
        };
        // Declare the chart dimensions and margins.
        const width = 640;
        const height = 300 * this.dataset.sections.length;
        const marginTop = 20;
        const marginRight = 20;
        const marginBottom = 30;
        const marginLeft = 40;

        this.plot_div.empty();
        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "A prisma diagram.")
            .attr("class", "d3")
            .attr("width", width)
            .attr("height", height)
            .node();
        this.vis = d3.select(this.svg).append("g");

        this.dataset.sections.map(section => {
            this.build_section(section);
        });
    }
}

export default PrismaPlot;
