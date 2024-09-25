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

    build_section(obj, idx) {
        // TODO: set position of g for each row
        const section_y = this.row_height * idx
        const section = this.vis.append("g")
            .attr("height", this.row_height)
            .attr("transform", "translate(0, " + section_y + ")");
        section.append("rect")
            .attr("transform", `translate(${obj.rx}, ${obj.ry})`)
            .attr("width", obj.width)
            .attr("height", obj.height)
            .style("fill", obj.bg_color)
            .style("border-width", obj.border_width)
            .attr("stroke", obj.border_color);
        // TODO: apply obj.text_style
        section.append("text")
            .attr("transform", `translate(${obj.rx + 5}, ${obj.ry + 15})`)
            .text(obj.name)
            .attr("class", "prisma_section_text")
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", 2)
            .style("font-color", obj.font_color);

        var box_index = 0;
        this.dataset.boxes.forEach(box => {
            if (box.section == obj.key) {
                const box_parent = section.append("g")
                    .attr("transform", `translate(${obj.rx + this.col_width * box_index}, ${obj.ry})`);
                this.build_box(box, box_parent);
                box_index++;
            }
        });
    }

    apply_text_style(obj, style) {
        // check style string for options like bold and left justified
    }

    build_box(obj, parent) {
        const box = parent.append("g");
        box.append("rect")
            .attr("transform", `translate(${obj.rx}, ${obj.ry})`)
            .attr("width", obj.width)
            .attr("height", obj.height)
            .style("fill", obj.bg_color)
            .style("border-width", obj.border_width)
            .attr("stroke", obj.border_color);
        box.append("text")
            .attr("x", obj.rx + 5)
            .attr("y", obj.ry + 15)
            .attr("width", obj.width)
            .attr("height", obj.height)
            .text(`${obj.name}: ${obj.count}`)
            .attr("class", "prisma_box_text")
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", 2)
            .style("font-color", obj.font_color);
    }

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
                    width: 250,
                    height: 100,
                    border_width: 2,
                    rx: 40,
                    ry: 10,
                    bg_color: "yellow",
                    border_color: "Black",
                    font_color: "Black",
                    text_style: "Left justified",
                },
                {
                    key: "section2key",
                    name: "Section 2",
                    width: 550,
                    height: 100,
                    border_width: 2,
                    rx: 40,
                    ry: 10,
                    bg_color: "white",
                    border_color: "Black",
                    font_color: "Black",
                    text_style: "Bold",
                },
            ],
            boxes: [{
                    key: "box1key",
                    name: "Included References",
                    width: 200,
                    height: 60,
                    border_width: 0,
                    rx: 20,
                    ry: 20,
                    bg_color: "white",
                    border_color: "black",
                    font_color: "",
                    text_style: "",
                    section: "section1key",
                    count: 30,
                },
                {
                    key: "box2key",
                    name: "Included References",
                    width: 200,
                    height: 60,
                    border_width: 0,
                    rx: 20,
                    ry: 20,
                    bg_color: "white",
                    border_color: "black",
                    font_color: "",
                    text_style: "",
                    section: "section2key",
                    count: 30,
                },
                {
                    key: "box3key",
                    name: "Excluded References",
                    width: 200,
                    height: 60,
                    border_width: 0,
                    rx: 20,
                    ry: 20,
                    bg_color: "white",
                    border_color: "black",
                    font_color: "",
                    text_style: "",
                    section: "section2key",
                    count: 30,
                }
            ],
            bulleted_lists: [],
            cards: [],
            arrows: [],
        };
        // Declare the chart dimensions and margins.
        this.col_width = 300;
        this.row_height = 200;
        this.width = 640;
        this.height = this.row_height * this.dataset.sections.length;
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
            .attr("width", this.width)
            .attr("height", this.height)
            .node();
        this.vis = d3.select(this.svg).append("g");

        this.dataset.sections.forEach((section, idx) => {
            this.build_section(section, idx);
        });
    }
}

export default PrismaPlot;
