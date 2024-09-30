import * as d3 from "d3";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import * as d3Arrow from "d3-arrow";

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

   makeGroupTextVisible(node) {
        for (let child of node.children) {
            child = this.getGroup(child.id);
            this.makeGroupTextVisible(child);
        }
        this.updateNodeTextAttributes(node, { "display": "inline" });
    }

    // should only be vertical adjustments
    resizeNodes(node) {
        node = this.getGroup(node.id);
        this.makeGroupTextVisible(node);
        let nodeSpacing = parseFloat(node.styling["spacing-vertical"]);

        // adjust position of vertical nodes when the previous node is part of a separate group
        if (node.isVertical && !node.parent) {
            let prevNodeGroup = node.previous;
            while (prevNodeGroup.parent) {
                prevNodeGroup = prevNodeGroup.parent;
            }
            prevNodeGroup = prevNodeGroup.group.getBBox();
            node.rect.setAttribute("y", prevNodeGroup.y + prevNodeGroup.height + nodeSpacing);
            this.updateNodeTextAttributes(node, { "y": prevNodeGroup.y + prevNodeGroup.height + nodeSpacing + this.TEXT_OFFSET_Y });
        }

        // wrap and push down all immediate text elements
        let width = node.rect.getBBox().width - parseFloat(node.styling["text-padding-x"]) - 5;
        for (let i = 0; i < node.text.length; i++) {
            HAWCUtils.wrapText(node.text[i], width);
            for (let j = i + 1; j < node.text.length; j++) {
                let previousTextY = node.text[j - 1].getBBox().y + node.text[j - 1].getBBox().height;
                node.text[j].setAttribute("y", previousTextY + this.TEXT_OFFSET_Y);
            }
        }

        // push children down
        for (let child of node.children) {
            child = this.getGroup(child.id);
            if (child.isVertical) {
                let prevChildBBox = child.previous.group.getBBox();
                let prevChildNodeSpacing = parseFloat(child.previous.styling["spacing-vertical"]);

                child.rect.setAttribute("y", prevChildBBox.y + prevChildBBox.height + prevChildNodeSpacing);
                this.updateNodeTextAttributes(child, { "y": prevChildBBox.y + prevChildBBox.height + prevChildNodeSpacing + this.TEXT_OFFSET_Y });
            }
            else if (child.previous) {
                let prevBBox = child.previous.rect.getBBox();
                child.rect.setAttribute("y", prevBBox.y);
                this.updateNodeTextAttributes(child, { "y": prevBBox.y + this.TEXT_OFFSET_Y });
            }
            else {
                let prevChildBBox = node.text[node.text.length - 1].getBBox();
                child.rect.setAttribute("y", prevChildBBox.y + prevChildBBox.height + 15);
                this.updateNodeTextAttributes(child, { "y": prevChildBBox.y + prevChildBBox.height + this.TEXT_OFFSET_Y + 15 });
            }
            this.resizeNodes(child);
        }

        // rect visual height adjustment
        if (node.rect.getAttribute("fixed-height") == "true") {
            //return node;
        }
        else if (Math.floor(node.group.getBBox().height) <= this.MIN_HEIGHT) {
            node.rect.setAttribute("height", this.MIN_HEIGHT);
        }
        else {
            node.rect.setAttribute("height", node.group.getBBox().height + 15);
        }
        return node;
    }

    getGroup(id) {
        let group = document.getElementById(id);
        if (!group) {
            return undefined;
        }
        let rect = document.getElementById(id + "-box");
        let text = $(document.getElementById(group.id)).children("text");
        let parent = group.parentElement.closest(".node");
        let previous = document.getElementById(group.getAttribute("previous"));
        let children = $(document.getElementById(group.id)).children(".node");
        let styling = JSON.parse(group.getAttribute("data-styling"));
        let isVertical = group.getAttribute("is-vertical");
        return {
            "id": id,
            "group": group,
            "rect": rect,
            "text": text,
            "styling": styling,
            "isVertical": (isVertical == "true"),
            "parent": this.getGroup(parent?.id),
            "previous": this.getGroup(previous?.id),
            "children": children
        }
    }

    // update attributes to all text elements within a node
    updateNodeTextAttributes(node, attr = {}) {
        node = this.getGroup(node.id);
        for (let text of node.text) {
            for (const [key, value] of Object.entries(attr)) {
                text.setAttribute(key, value);
            }
        }
    }

    // return a group with rect and text child elements
    createRectangleWithText(id = "", text = "", x = 0, y = 0, styling = {}) {
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        let group = document.createElementNS(this.NAMESPACE, "g");
        group.setAttribute("id", id);
        group.setAttribute("class", "node");
        group.setAttribute("data-styling", JSON.stringify(styling));

        let rect = document.createElementNS(this.NAMESPACE, "rect");
        rect.setAttribute("x", x);
        rect.setAttribute("y", y);
        rect.setAttribute("class", "node-rect");
        rect.setAttribute("id", id + "-box");
        if (styling.width == 0) {
            rect.setAttribute("width", this.MAX_WIDTH);
            rect.setAttribute("fixed-width", false);
        }
        else {
            rect.setAttribute("width", styling.width);
            rect.setAttribute("fixed-width", true);
        }
        if (styling.height == 0) {
            rect.setAttribute("height", this.MIN_HEIGHT);
            rect.setAttribute("fixed-height", false);
        }
        else {
            rect.setAttribute("height", styling.height);
            rect.setAttribute("fixed-height", true);
        }
        rect.setAttribute("rx", styling.rx);
        rect.setAttribute("ry", styling.ry);
        rect.style["fill"] = styling["bg-color"];
        rect.style["stroke"] = styling["stroke"];
        rect.style["stroke-width"] = styling["stroke-width"];

        group.appendChild(rect);
        return {
            "id": id,
            "group": group,
            "rect": rect,
            "text": text,
            "styling": styling
        };
    }

    addTextToNode(node, id, text, styling = {}) {
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        node = this.getGroup(node.id);
        let x = node.rect.getBBox().x;
        let y = node.rect.getBBox().y;

        let textElement = document.createElementNS(this.NAMESPACE, "text");
        textElement.setAttribute("data-styling", JSON.stringify(styling));
        textElement.setAttribute("x", x + this.TEXT_OFFSET_X + parseFloat(styling["text-padding-x"]));
        textElement.setAttribute("y", y + this.TEXT_OFFSET_Y);
        textElement.setAttribute("display", "none");
        textElement.setAttribute("id", id);
        textElement.setAttribute("font-size", this.TEXT_SIZE + parseFloat(styling["text-size"]) + "em");
        textElement.setAttribute("font-weight", styling["text-style"]);
        textElement.style["fill"] = styling["text-color"];
        textElement.innerHTML = text;

        node.group.appendChild(textElement);
        return textElement;
    }

    addNodeToHTML(node, parent = undefined) {
        if (parent) {
            $(document.getElementById(parent.id)).append(node.group);
        }
        else {
            $("#svgworkspace").append(node.group);
        }
        let txtEle = this.addTextToNode(node, node.id + "-text", node.text, node.styling);
        node.text = txtEle;

        node.rect.onclick = this.nodeOnClick;
        txtEle.onclick = this.nodeOnClick;
        return node;
    }

    // styling applied after the diagram is draw but before arrows are calculated
    // general box position, text-padding-y
    applyPostStyling() {
        let allNodes = document.getElementsByClassName("node");
        for (let node of allNodes) {
            node = this.getGroup(node.id);

            // re-position boxes
            let nodePadX = JSON.parse(node.styling["x"]);
            let nodePadY = JSON.parse(node.styling["y"]);
            node.rect.setAttribute("x", node.rect.getBBox().x + nodePadX);
            node.rect.setAttribute("y", node.rect.getBBox().y + nodePadY);

            // text padding y styling
            let textPaddingY = JSON.parse(node.styling["text-padding-y"]);
            for (let txt of node.text) {
                let tspanArray = $(document.getElementById(txt.id)).children("tspan");
                for (let tspan of tspanArray) {
                    let currentY = parseFloat(tspan.getAttribute("y"));
                    tspan.setAttribute("x", parseFloat(tspan.getAttribute("x")) + nodePadX);
                    tspan.setAttribute("y", currentY + nodePadY + parseFloat(textPaddingY));
                }
            }
        }
    }

    // https://github.com/HarryStevens/d3-arrow
    // https://observablehq.com/d/7759e56ba89ced03
    drawConnection(id1, id2, styling = {}) {
        let id = id1 + id2;
        let node1BBox = this.getGroup(id1).rect.getBBox();
        let node2BBox = this.getGroup(id2).rect.getBBox();

        // same x = vertical
        if (node1BBox.x == node2BBox.x || styling["arrow-force-vertical"] == "true") {
            let yMidpoint = (node2BBox.y - (node1BBox.y + node1BBox.height)) / 2;
            yMidpoint = node1BBox.y + node1BBox.height + yMidpoint;

            let node1XY = [
                node1BBox.x + node1BBox.width / 2,
                node1BBox.y + node1BBox.height
            ];
            let node1Midpoint = [
                node1BBox.x + node1BBox.width / 2,
                yMidpoint
            ];
            this.connectPoints(id + "_1", node1XY, node1Midpoint, false, styling);

            let node2Midpoint = [
                node2BBox.x + node2BBox.width / 2,
                yMidpoint
            ];
            this.connectPoints(id + "_2", node1Midpoint, node2Midpoint, false, styling);

            let node2XY = [
                node2BBox.x + node2BBox.width / 2,
                node2BBox.y
            ];
            this.connectPoints(id + "_3", node2Midpoint, node2XY, true, styling);
        }
        else {
            let xMidpoint = (node2BBox.x - (node1BBox.x + node1BBox.width)) / 2;
            xMidpoint = node1BBox.x + node1BBox.width + xMidpoint;

            let node1XY = [
                node1BBox.x + node1BBox.width,
                node1BBox.y + node1BBox.height / 2
            ];
            let node1Midpoint = [
                xMidpoint,
                node1BBox.y + node1BBox.height / 2
            ];
            this.connectPoints(id + "_1", node1XY, node1Midpoint, false, styling);

            let node2Midpoint = [
                xMidpoint,
                node2BBox.y + node2BBox.height / 2
            ];
            this.connectPoints(id + "_2", node1Midpoint, node2Midpoint, false, styling);

            let node2XY = [
                node2BBox.x,
                node2BBox.y + node2BBox.height / 2
            ];
            this.connectPoints(id + "_3", node2Midpoint, node2XY, true, styling);
        }
    }

    connectPoints(id, xy1, xy2, arrowhead = true, styling = {}) {
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }
        let arrowType = "arrow" + styling["arrow-type"];
        let d3svg = d3.select("#svgworkspace");
        let arrow = d3Arrow[arrowType]().id(id);
        if (arrowhead) {
            arrow.attr("stroke", styling["arrow-color"]).attr("stroke-width", styling["arrow-width"]);
        }
        else {
            arrow.attr("fill", "transparent").attr("stroke", "transparent");
        }
        d3svg.call(arrow);
        d3svg.append("polyline")
            .attr("marker-end", `url(#${id})`)
            .attr("points", [xy1, xy2])
            .attr("stroke", styling["arrow-color"])
            .attr("stroke-width", styling["arrow-width"]);
    }

    initNode(id, text, styling = {}) {
        let initialNode = this.createRectangleWithText(
            id,
            text,
            this.WORKSPACE_START_X,
            this.WORKSPACE_START_Y,
            styling
        );
        return this.addNodeToHTML(initialNode);
    }

    createNewVerticalNode(prevNode, id, text, group = false, styling = {}) {
        prevNode = this.getGroup(prevNode.id);
        let prevBBox = prevNode.rect.getBBox();
        let nodeSpacing = styling["spacing-vertical"] ? parseFloat(styling["spacing-vertical"]) : this.SPACING_V;
        let y = prevBBox.y + prevBBox.height + nodeSpacing;

        let verticalNode = this.createRectangleWithText(id, text, prevBBox.x, y, styling);
        verticalNode.group.setAttribute("previous", prevNode.id);
        verticalNode.group.setAttribute("is-vertical", true);

        if (group) {
            return this.addNodeToHTML(verticalNode, prevNode.parent);
        }
        return this.addNodeToHTML(verticalNode);
    }

    // group nodes if prevNode has a parent
    createNewHorizontalNode(prevNode, id, text, group = false, styling = {}) {
        prevNode = this.getGroup(prevNode.id);
        let prevBBox = prevNode.rect.getBBox();
        let x;
        let nodeSpacing = styling["spacing-horizontal"] ? parseFloat(styling["spacing-horizontal"]) : this.SPACING_H;
        if (prevNode.parent && !group) {
            x = prevNode.parent.rect.getBBox().width + nodeSpacing;
        }
        else {
            x = prevBBox.x + prevBBox.width + nodeSpacing;
        }
        let horizontalNode = this.createRectangleWithText(id, text, x, prevBBox.y, styling);
        horizontalNode.group.setAttribute("previous", prevNode.id);
        horizontalNode = this.addNodeToHTML(horizontalNode, prevNode.parent);

        if (group) {
            let parent = prevNode.parent;
            while (parent) {
                if (parent.styling["width"] == "0") {
                    let parentAdjustedWidth = parent.group.getBBox().width + 15;
                    parent.rect.setAttribute("width", parentAdjustedWidth);
                }
                parent = this.getGroup(parent.id).parent;
            }
        }
        return horizontalNode;
    }

    createChildNode(parent, id, text, styling = {}) {
        let pad = 15;
        let parentBBox = parent.rect.getBBox();

        let childAdjustedY = parentBBox.y + pad;
        let childAdjustedX = parentBBox.x + pad;
        let child = this.createRectangleWithText(id, text, childAdjustedX, childAdjustedY, styling);

        let currentParent = parent;
        while (currentParent) {
            if (currentParent.styling["width"] == "0") {
                parentBBox = currentParent.rect.getBBox();
                let parentAdjustedWidth = parentBBox.width + pad * 2;
                currentParent.rect.setAttribute("width", parentAdjustedWidth);
            }
            currentParent = this.getGroup(currentParent.id).parent;
        }

        return this.addNodeToHTML(child, parent);
    }

    nodeOnClick(e) {
        let id = e.target.parentNode.id.replace(new RegExp("-box" + '$'), '');
        id = id.replace(new RegExp("-text" + '$'), '');
        let node = this.getGroup(id);
        console.log(node);
    }

    // child node with its own styling defaults
    // also checks if card can fit on row
    createCard(parent, text, styling = {}) {
        let cardMinHeight = 70;
        const CARD_DEFAULT = {
            "width": "100",
            "spacing-horizontal": "20",
            "spacing-vertical": "10"
        }
        // first inherit from card default then style default
        for (const [key, value] of Object.entries(CARD_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        let allCards = $(document.getElementById(parent.group.id)).children(".node");
        let prevNode = (allCards.length > 0) ? allCards[allCards.length - 1] : parent;
        prevNode = this.getGroup(prevNode.id);
        let id = parent.id + "_" + allCards.length;

        this.cardrowlength++;
        if (allCards.length > 0) {
            let parentPosition = parent.rect.getBBox().x + parent.rect.getBBox().width;
            let prevCardPosition = prevNode.rect.getBBox().x + prevNode.rect.getBBox().width;
            let cardPosition = prevCardPosition + parseFloat(styling["spacing-horizontal"]) + parseFloat(styling["width"]);

            if (cardPosition < parentPosition) {
                return this.createNewHorizontalNode(prevNode, id, text, true, styling);
            }
            else { // new row
                prevNode = allCards[allCards.length - this.cardrowlength];
                this.cardrowlength = 0;
                return this.createNewVerticalNode(prevNode, id, text, true, styling);
            }
        }
        this.cardrowlength = 0;
        return this.createChildNode(parent, id, text, styling);
    }

    // helper function for parsing the data structure
    // handles list/card layouts at the section and block level
    listCardLayout(id, col) {
        let blocks = col.blocks || col.sub_blocks;
        let currentNode = this.getGroup(id);

        if (col.block_layout == "list") {
            for (let i = 0; i < blocks.length; i++) {
                let blockStyle = blocks[i].styling ?? {};
                if (!blockStyle["text-padding-x"]) blockStyle["text-padding-x"] = "5";

                let subblockId = currentNode.id + "-text_" + i;
                let subblockText = this.HTML_BULLET + ` ${blocks[i].label}: ${blocks[i].value}`;

                let txtEle = this.addTextToNode(currentNode, subblockId, subblockText, blockStyle);
                txtEle.onclick = (e) => { console.log(blocks[i]) };
            }
        }
        else {
            for (let subblock of blocks) {
                let blockStyle = subblock.styling ?? {};
                this.createCard(currentNode, subblock.label, blockStyle);
            }
        }
    }

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

        this.NAMESPACE = "http://www.w3.org/2000/svg";
        this.HTML_BULLET = "&#8226;";
        this.WORKSPACE_START_X = 20; // first box always placed here
        this.WORKSPACE_START_Y = 20;
        this.MAX_WIDTH = 300; // box dimensions
        this.MIN_HEIGHT = 100;
        this.SPACING_V = 100; // distance between boxes
        this.SPACING_H = 120;
        this.TEXT_OFFSET_X = 10;
        this.TEXT_OFFSET_Y = 20;
        this.TEXT_SIZE = 1;
        this.STYLE_DEFAULT = {
            "x": "0", // +- centered around current box position (moves relevant text as well)
            "y": "0",
            "width": "0", // non-0 value for fixed
            "height": "0",
            "spacing-horizontal": this.SPACING_H,
            "spacing-vertical": this.SPACING_V,
            "text-padding-x": "0", // +- centered around global text offset values
            "text-padding-y": "0",
            "text-color": "black",
            "text-style": "normal", // or "bold"
            "text-size": "0", // always appends "em" unit, +- centered around global text size
            "bg-color": "white",
            "stroke": "black", // box border color
            "stroke-width": "3", // box border width
            "rx": "20", // box rounded edge horizontal
            "ry": "20", // / box rounded edge vertical
            "arrow-color": "black",
            "arrow-width": "2",
            "arrow-type": "1", // valid: 1,2,3,5,10,11,13
            "arrow-force-vertical": "false"
        }

        this.plot_div.empty()
        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "An exploratory heatmap graphic")
            .attr("class", "d3")
            .attr("id", "svgworkspace")
            .attr("width", "100%")
            .attr("height", "2000")
            .node();
        this.cardrowlength = -1;
        // Examples
        // Hero litflow diagram: https://hero.epa.gov/hero/index.cfm/litflow/viewProject/project_id/2489
        // https://hawcproject.org/summary/visual/assessment/405/eFigure-1-Reference-Flow-Diagram/
        // figure one: https://www.bmj.com/content/372/bmj.n71
        // https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8958186/figure/cl21230-fig-0003/


        // NOTE changed sub_block_layout to just block_layout and added as optional to section level
        let diagramSections = [
            {
                "label": "Records",
                "key": "Records",
                "block_layout": "card",
                "styling": {
                    "width": this.MAX_WIDTH * 2 + this.SPACING_H + 30,
                },
                "blocks": [
                    {
                        "label": "Source 1",
                        "key": "Source 1",
                        "value": "",
                        "styling": { "text-color": "red", "width": "200" }
                    },
                    {
                        "label": "Source 2",
                        "key": "Source 2",
                        "value": "",
                    },
                    {
                        "label": "Source 3",
                        "key": "Source 3",
                        "value": "",
                    },
                    {
                        "label": "Source 4",
                        "key": "Source 4",
                        "value": "",
                    },
                    {
                        "label": "Source 5",
                        "key": "Source 5",
                        "value": "",
                    },
                    {
                        "label": "Source 6",
                        "key": "Source 6",
                        "value": "",
                    },
                    {
                        "label": "Source 7",
                        "key": "Source 7",
                        "value": "",
                    },
                    {
                        "label": "Source 8",
                        "key": "Source 8",
                        "value": "",
                    },
                    {
                        "label": "Source 9",
                        "key": "Source 9",
                        "value": "",
                    },
                    /*
                    {
                        "label": "References identified",
                        "tags": ["Included", "Excluded"],
                        "count": "unique_sum",
                        "value": 13725,
                        "refs": '[...]',
                    }*/
                ],
            },
            {
                "label": "TIAB",
                "key": "TIAB",
                "blocks": [
                    {
                        "label": "References screened",
                        "key": "References screened",
                        "tags": [
                            "Included",
                            "Excluded|Manually excluded in Distiller (full-text)",
                            "Excluded|Manually excluded in SWIFT-Review",
                            "Excluded|Automatically excluded via ML in SWIFT-Active Screener",
                            "Excluded|Manually excluded in Distiller (TIAB)",
                        ],
                        "count": "unique_sum",
                        "value": 13725,
                        "refs": '[...]',
                    },
                    {
                        "label": "References excluded",
                        "key": "References excluded",
                        "tags": [
                            "Excluded|Manually excluded in SWIFT-Review",
                            "Excluded|Automatically excluded via ML in SWIFT-Active Screener",
                            "Excluded|Manually excluded in Distiller (TIAB)",
                        ],
                        "count": "unique_sum",
                        "value": 13189,
                        "refs": '[...]',
                        "styling": {
                            "y": "-30",
                            "x": "-50",
                        }
                    },
                ],
            },
            {
                "label": "FT",
                "key": "FT",
                "blocks": [
                    {

                        "label": "References screened",
                        "key": "References screened",
                        "tags": [
                            "Included",
                            "Excluded|Manually excluded in Distiller (full-text)",
                        ],
                        "count": "unique_sum",
                        "value": 541,
                        "refs": '[...]',
                    },
                    {
                        "label": "References excluded",
                        "key": "References excluded",
                        "tags": [
                            "Excluded|Manually excluded in Distiller (full-text)|Unable to obtain full-text"
                        ],
                        "count": "unique_sum",
                        "value": 32,
                        "refs": '[...]',
                    },
                ],
            },
            {
                "label": "FT - eligible",
                "key": "FT - eligible",
                "styling": {
                    "bg-color": "grey",
                    "text-padding-x": "315",
                    "text-padding-y": "20",
                    "text-size": ".3",
                    "text-style": "bold"
                },
                "blocks": [
                    {
                        "label": "References screened",
                        "key": "References screened",
                        "tags": [
                            "Included",
                            "Excluded|Manually excluded in Distiller (full-text)|No data provided",
                            "Excluded|Manually excluded in Distiller (full-text)|No relevant exposure",
                            "Excluded|Manually excluded in Distiller (full-text)|Wildlife study",
                        ],
                        "count": "unique_sum",
                        "value": 509,
                        "refs": '[...]',
                        "styling": {
                            "text-color": "white",
                            "bg-color": "green",
                            "stroke": "blue",
                            "stroke-width": "10",
                            "rx": "0",
                            "ry": "0"
                        },
                    },
                    {
                        "label": "References excluded",
                        "key": "References excluded",
                        "block_layout": "list",
                        "styling": {
                            "height": this.MIN_HEIGHT
                        },
                        "sub_blocks": [
                            {
                                "label": "No data provided",
                                "key": "No data provided",
                                "tags": [
                                    "Excluded|Manually excluded in Distiller (full-text)|No data provided"
                                ],
                                "count": "unique_sum",
                                "value": 4,
                                "refs": '[...]',
                                "styling": { "text-color": "red" }
                            },
                            {
                                "label": "No relevant exposure",
                                "key": "No relevant exposure",
                                "tags": [
                                    "Excluded|Manually excluded in Distiller (full-text)|No relevant exposure"
                                ],
                                "count": "unique_sum",
                                "value": 146,
                                "refs": '[...]',
                            },
                            {
                                "label": "Wildlife study",
                                "key": "Wildlife study",
                                "tags": [
                                    "Excluded|Manually excluded in Distiller (full-text)|Wildlife study"
                                ],
                                "count": "unique_sum",
                                "value": 4,
                                "refs": '[...]',
                            },
                        ],
                        "count": "unique_sum",
                        "value": 150,
                        "refs": '[...]',
                    },
                ],
            },
            {
                "label": "Included studies",
                "key": "Included studies",
                "blocks": [
                    {
                        "label": "Results",
                        "key": "Results",
                        "tags": ["Included"],
                        "count": "unique_sum",
                        "value": 359,
                        "refs": '[...]',
                    }
                ],
            },
        ]


        // parse data structure
        let parent;
        let child;
        let sibling;
        for (let row of diagramSections) {
            let blockId = `${row.key}`.replace(/ /g, '');
            let blockBoxInfo = row.label;
            let sectionStyle = row.styling ?? {};
            if (!parent) {
                parent = this.initNode(blockId, blockBoxInfo, sectionStyle);
            }
            else {
                parent = this.createNewVerticalNode(parent, blockId, blockBoxInfo, false, sectionStyle);
            }

            if (row.block_layout) {
                this.listCardLayout(blockId, row);
                this.resizeNodes(parent);
                continue;
            }

            for (let i = 0; i < row.blocks.length; i++) {
                let col = row.blocks[i];
                let id = `${row.key}.${col.key}`.replace(/ /g, '');
                let boxInfo = col.label + ": " + col.value;
                let blockStyle = col.styling ?? {};

                if (i > 0) {
                    let previous = sibling || child;
                    sibling = this.createNewHorizontalNode(previous, id, boxInfo, true, blockStyle);
                }
                else {
                    child = this.createChildNode(parent, id, boxInfo, blockStyle);
                    sibling = undefined;
                }

                if (col.sub_blocks) {
                    this.listCardLayout(id, col);
                }
            }
            this.resizeNodes(parent);
        }

        this.applyPostStyling();

        // NOTE changed separator from | to .
        // NOTE removed "type"
        let connections = [
            {
                "src": "Records",
                "dst": "TIAB",
                "styling": {
                    "arrow-type": "11"
                }
            },
            {
                "src": "TIAB.References screened",
                "dst": "TIAB.References excluded",
            },
            {
                "src": "TIAB.References screened",
                "dst": "FT.References excluded",
                "styling": {
                    "arrow-force-vertical": "true"
                }
            },
            {
                "src": "TIAB.References screened",
                "dst": "FT.References screened",
                "styling": {
                    "arrow-color": "blue",
                    "arrow-width": "6",
                }
            },
            {
                "src": "FT.References screened",
                "dst": "FT - eligible.References screened",
            },
            {
                "src": "FT - eligible.References screened",
                "dst": "FT - eligible.References excluded",
            },
            {
                "src": "FT - eligible.References screened",
                "dst": "Included studies.Results",
            }
        ]

        for (let connection of connections) {
            let srcId = connection.src.replace(/ /g, '');
            let dstId = connection.dst.replace(/ /g, '');
            this.drawConnection(srcId, dstId, connection.styling);
        }

    }
}

export default PrismaPlot;
