import * as d3 from "d3";
import * as d3Arrow from "d3-arrow";
import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";
import VisualToolbar from "shared/components/VisualToolbar";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

const NAMESPACE = "http://www.w3.org/2000/svg",
    WORKSPACE_START_X = 20,
    WORKSPACE_START_Y = 20,
    getGroup = function(id) {
        let group = document.getElementById(id);
        if (!group) {
            return undefined;
        }
        let rect = document.getElementById(id + "-box"),
            text = $(document.getElementById(group.id)).children("text"),
            parent = group.parentElement.closest(".node"),
            previous = document.getElementById(group.getAttribute("previous")),
            children = $(document.getElementById(group.id)).children(".node"),
            styling = JSON.parse(group.getAttribute("data-styling")),
            isVertical = group.getAttribute("is-vertical");
        return {
            id,
            group,
            rect,
            text,
            styling,
            isVertical: isVertical == "true",
            parent: getGroup(parent?.id),
            previous: getGroup(previous?.id),
            children,
        };
    },
    updateNodeTextAttributes = function(node, attr = {}) {
        // update attributes to all text elements within a node
        node = getGroup(node.id);
        for (let text of node.text) {
            for (const [key, value] of Object.entries(attr)) {
                text.setAttribute(key, value);
            }
        }
    },
    makeGroupTextVisible = function(node) {
        for (let child of node.children) {
            child = getGroup(child.id);
            makeGroupTextVisible(child);
        }
        updateNodeTextAttributes(node, {display: "inline"});
    },
    nodeOnClick = function(e) {
        let id = e.target.parentNode.id.replace(new RegExp("-box" + "$"), "");
        id = id.replace(new RegExp("-text" + "$"), "");
        let node = getGroup(id);
        alert(node);
    };

class PrismaPlot {
    // Examples
    // https://hero.epa.gov/hero/index.cfm/litflow/viewProject/project_id/2489
    // https://hawcproject.org/summary/visual/assessment/405/eFigure-1-Reference-Flow-Diagram/
    // https://www.bmj.com/content/372/bmj.n71
    // https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8958186/figure/cl21230-fig-0003/
    constructor(store, options) {
        this.modal = new HAWCModal();
        this.store = store;
        this.options = options;
    }

    render(div) {
        this.plot_div = $(div);
        this.build_plot();
    }

    resizeNodes(node) {
        // should only be vertical adjustments
        node = getGroup(node.id);
        makeGroupTextVisible(node);
        let nodeSpacing = parseFloat(node.styling["spacing-vertical"]);

        // adjust position of vertical nodes when the previous node is part of a separate group
        if (node.isVertical && !node.parent) {
            let prevNodeGroup = node.previous;
            while (prevNodeGroup.parent) {
                prevNodeGroup = prevNodeGroup.parent;
            }
            prevNodeGroup = prevNodeGroup.group.getBBox();
            node.rect.setAttribute("y", prevNodeGroup.y + prevNodeGroup.height + nodeSpacing);
            updateNodeTextAttributes(node, {
                y: prevNodeGroup.y + prevNodeGroup.height + nodeSpacing + this.TEXT_OFFSET_Y,
            });
        }

        // wrap and push down all immediate text elements
        let width = node.rect.getBBox().width - parseFloat(node.styling["text-padding-x"]) - 5;
        for (let i = 0; i < node.text.length; i++) {
            HAWCUtils.wrapText(node.text[i], width);
            for (let j = i + 1; j < node.text.length; j++) {
                let bb = node.text[j - 1].getBBox(),
                    previousTextY = bb.y + bb.height;
                node.text[j].setAttribute("y", previousTextY + this.TEXT_OFFSET_Y);
            }
        }

        // push children down
        for (let child of node.children) {
            child = getGroup(child.id);
            if (child.isVertical) {
                let prevChildBBox = child.previous.group.getBBox(),
                    prevChildNodeSpacing = parseFloat(child.previous.styling["spacing-vertical"]);

                child.rect.setAttribute(
                    "y",
                    prevChildBBox.y + prevChildBBox.height + prevChildNodeSpacing
                );
                updateNodeTextAttributes(child, {
                    y:
                        prevChildBBox.y +
                        prevChildBBox.height +
                        prevChildNodeSpacing +
                        this.TEXT_OFFSET_Y,
                });
            } else if (child.previous) {
                let prevBBox = child.previous.rect.getBBox();
                child.rect.setAttribute("y", prevBBox.y);
                updateNodeTextAttributes(child, {y: prevBBox.y + this.TEXT_OFFSET_Y});
            } else {
                let prevChildBBox = node.text[node.text.length - 1].getBBox();
                child.rect.setAttribute("y", prevChildBBox.y + prevChildBBox.height + 15);
                updateNodeTextAttributes(child, {
                    y: prevChildBBox.y + prevChildBBox.height + this.TEXT_OFFSET_Y + 15,
                });
            }
            this.resizeNodes(child);
        }

        // rect visual height adjustment
        if (node.rect.getAttribute("fixed-height") == "true") {
            //return node;
        } else if (Math.floor(node.group.getBBox().height) <= this.MIN_HEIGHT) {
            node.rect.setAttribute("height", this.MIN_HEIGHT);
        } else {
            node.rect.setAttribute("height", node.group.getBBox().height + 15);
        }
        return node;
    }

    createRectangleWithText(id = "", text = "", x = 0, y = 0, styling = {}) {
        // return a group with rect and text child elements
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        let group = document.createElementNS(NAMESPACE, "g");
        group.setAttribute("id", id);
        group.setAttribute("class", "node");
        group.setAttribute("data-styling", JSON.stringify(styling));

        let rect = document.createElementNS(NAMESPACE, "rect");
        rect.setAttribute("x", x);
        rect.setAttribute("y", y);
        rect.setAttribute("class", "node-rect");
        rect.setAttribute("id", id + "-box");
        if (styling.width == 0) {
            rect.setAttribute("width", this.MAX_WIDTH);
            rect.setAttribute("fixed-width", false);
        } else {
            rect.setAttribute("width", styling.width);
            rect.setAttribute("fixed-width", true);
        }
        if (styling.height == 0) {
            rect.setAttribute("height", this.MIN_HEIGHT);
            rect.setAttribute("fixed-height", false);
        } else {
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
            id,
            group,
            rect,
            text,
            styling,
        };
    }

    addTextToNode(node, id, text, styling = {}) {
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        node = getGroup(node.id);
        let x = node.rect.getBBox().x;
        let y = node.rect.getBBox().y;

        let textElement = document.createElementNS(NAMESPACE, "text");
        textElement.setAttribute("data-styling", JSON.stringify(styling));
        textElement.setAttribute(
            "x",
            x + this.TEXT_OFFSET_X + parseFloat(styling["text-padding-x"])
        );
        textElement.setAttribute("y", y + this.TEXT_OFFSET_Y);
        textElement.setAttribute("display", "none");
        textElement.setAttribute("id", id);
        textElement.setAttribute(
            "font-size",
            this.TEXT_SIZE + parseFloat(styling["text-size"]) + "em"
        );
        textElement.setAttribute("font-weight", styling["text-style"]);
        textElement.style["fill"] = styling["text-color"];
        textElement.innerHTML = text;

        node.group.appendChild(textElement);
        return textElement;
    }

    addNodeToHTML(node, parent = undefined) {
        if (parent) {
            document.getElementById(parent.id).append(node.group);
        } else {
            this.svg.append(node.group);
        }
        let txtEle = this.addTextToNode(node, node.id + "-text", node.text, node.styling);
        node.text = txtEle;

        node.rect.onclick = nodeOnClick.bind(this);
        txtEle.onclick = nodeOnClick.bind(this);
        return node;
    }

    drawConnection(connection) {
        // https://github.com/HarryStevens/d3-arrow
        // https://observablehq.com/d/7759e56ba89ced03
        const id = connection.key,
            styling = _.clone(this.store.settings.styles),
            node1BBox = getGroup(connection.src).rect.getBBox(),
            node2BBox = getGroup(connection.dst).rect.getBBox();

        // add overrides (TODO - this isn't working yet, to fix)
        if (connection.styling) {
            _.merge(styling, connection.styling);
        }

        // same x = vertical
        if (node1BBox.x == node2BBox.x || styling["arrow-force-vertical"] == true) {
            let yMidpoint = (node2BBox.y - (node1BBox.y + node1BBox.height)) / 2;
            yMidpoint = node1BBox.y + node1BBox.height + yMidpoint;

            let node1XY = [node1BBox.x + node1BBox.width / 2, node1BBox.y + node1BBox.height];
            let node1Midpoint = [node1BBox.x + node1BBox.width / 2, yMidpoint];
            this.connectPoints(id + "_1", node1XY, node1Midpoint, false, styling);

            let node2Midpoint = [node2BBox.x + node2BBox.width / 2, yMidpoint];
            this.connectPoints(id + "_2", node1Midpoint, node2Midpoint, false, styling);

            let node2XY = [node2BBox.x + node2BBox.width / 2, node2BBox.y];
            this.connectPoints(id + "_3", node2Midpoint, node2XY, true, styling);
        } else {
            let xMidpoint = (node2BBox.x - (node1BBox.x + node1BBox.width)) / 2;
            xMidpoint = node1BBox.x + node1BBox.width + xMidpoint;

            let node1XY = [node1BBox.x + node1BBox.width, node1BBox.y + node1BBox.height / 2];
            let node1Midpoint = [xMidpoint, node1BBox.y + node1BBox.height / 2];
            this.connectPoints(id + "_1", node1XY, node1Midpoint, false, styling);

            let node2Midpoint = [xMidpoint, node2BBox.y + node2BBox.height / 2];
            this.connectPoints(id + "_2", node1Midpoint, node2Midpoint, false, styling);

            let node2XY = [node2BBox.x, node2BBox.y + node2BBox.height / 2];
            this.connectPoints(id + "_3", node2Midpoint, node2XY, true, styling);
        }
    }

    connectPoints(id, xy1, xy2, arrowhead = true, styling = {}) {
        for (const [key, value] of Object.entries(this.STYLE_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }
        let arrowType = "arrow" + styling["arrow-type"];
        let arrow = d3Arrow[arrowType]().id(id);
        if (arrowhead) {
            arrow
                .attr("stroke", styling["arrow-color"])
                .attr("stroke-width", styling["arrow-width"]);
        } else {
            arrow.attr("fill", "transparent").attr("stroke", "transparent");
        }
        d3.select(this.svg).call(arrow);
        d3.select(this.svg)
            .append("polyline")
            .attr("marker-end", `url(#${id})`)
            .attr("points", [xy1, xy2])
            .attr("stroke", styling["arrow-color"])
            .attr("stroke-width", styling["arrow-width"]);
    }

    createNewVerticalNode(prevNode, id, text, group = false, styling = {}) {
        prevNode = getGroup(prevNode.id);
        let prevBBox = prevNode.rect.getBBox();
        let nodeSpacing = styling["spacing-vertical"]
            ? parseFloat(styling["spacing-vertical"])
            : this.SPACING_V;
        let y = prevBBox.y + prevBBox.height + nodeSpacing;

        let verticalNode = this.createRectangleWithText(id, text, prevBBox.x, y, styling);
        verticalNode.group.setAttribute("previous", prevNode.id);
        verticalNode.group.setAttribute("is-vertical", true);

        if (group) {
            return this.addNodeToHTML(verticalNode, prevNode.parent);
        }
        return this.addNodeToHTML(verticalNode);
    }

    createNewHorizontalNode(prevNode, id, text, group = false, styling = {}) {
        // group nodes if prevNode has a parent
        prevNode = getGroup(prevNode.id);
        let prevBBox = prevNode.rect.getBBox();
        let x;
        let nodeSpacing = styling["spacing-horizontal"]
            ? parseFloat(styling["spacing-horizontal"])
            : this.SPACING_H;
        if (prevNode.parent && !group) {
            x = prevNode.parent.rect.getBBox().width + nodeSpacing;
        } else {
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
                parent = getGroup(parent.id).parent;
            }
        }
        return horizontalNode;
    }

    createChildNode(parent, id, text, styling = {}) {
        let pad = 15,
            parentBBox = parent.rect.getBBox(),
            childAdjustedY = parentBBox.y + pad,
            childAdjustedX = parentBBox.x + pad,
            child = this.createRectangleWithText(id, text, childAdjustedX, childAdjustedY, styling),
            currentParent = parent;
        while (currentParent) {
            if (currentParent.styling["width"] == "0") {
                parentBBox = currentParent.rect.getBBox();
                let parentAdjustedWidth = parentBBox.width + pad * 2;
                currentParent.rect.setAttribute("width", parentAdjustedWidth);
            }
            currentParent = getGroup(currentParent.id).parent;
        }

        return this.addNodeToHTML(child, parent);
    }

    createCard(parent, text, styling = {}) {
        // child node with its own styling defaults; also checks if card can fit on row
        const CARD_DEFAULT = {
            width: "100",
            "spacing-horizontal": "20",
            "spacing-vertical": "10",
        };
        // first inherit from card default then style default
        for (const [key, value] of Object.entries(CARD_DEFAULT)) {
            if (!styling[key]) styling[key] = value;
        }

        let allCards = $(document.getElementById(parent.group.id)).children(".node"),
            prevNode = allCards.length > 0 ? allCards[allCards.length - 1] : parent,
            id = parent.id + "_" + allCards.length;
        prevNode = getGroup(prevNode.id);

        this.cardrowlength++;
        if (allCards.length > 0) {
            let parentPosition = parent.rect.getBBox().x + parent.rect.getBBox().width,
                prevCardPosition = prevNode.rect.getBBox().x + prevNode.rect.getBBox().width,
                cardPosition =
                    prevCardPosition +
                    parseFloat(styling["spacing-horizontal"]) +
                    parseFloat(styling["width"]);

            if (cardPosition < parentPosition) {
                return this.createNewHorizontalNode(prevNode, id, text, true, styling);
            } else {
                // new row
                prevNode = allCards[allCards.length - this.cardrowlength];
                this.cardrowlength = 0;
                return this.createNewVerticalNode(prevNode, id, text, true, styling);
            }
        }
        this.cardrowlength = 0;
        return this.createChildNode(parent, id, text, styling);
    }

    drawBox(id, col) {
        // helper function for parsing the data structure
        // handles list/card layouts at the section and block level
        let blocks = col.blocks || col.sub_blocks,
            currentNode = getGroup(id);

        if (col.block_layout == "list") {
            for (let i = 0; i < blocks.length; i++) {
                let blockStyle = blocks[i].styling ?? {},
                    subblockId = currentNode.id + "-text_" + i,
                    subblockText = `• ${blocks[i].label}: ${blocks[i].value}`;

                if (!blockStyle["text-padding-x"]) {
                    blockStyle["text-padding-x"] = "5";
                }

                let txtEle = this.addTextToNode(currentNode, subblockId, subblockText, blockStyle);
                txtEle.onclick = e => {
                    alert(blocks[i]);
                };
            }
        } else {
            for (let subblock of blocks) {
                let blockStyle = subblock.styling ?? {};
                this.createCard(currentNode, subblock.label, blockStyle);
            }
        }
    }

    addResizeAndToolbar() {
        const nativeSize = {
                width: this.w + 40,
                height: this.h + 40,
            },
            div = $("<div>")
                .css({
                    position: "relative",
                    display: "block",
                    top: "-30px",
                    left: "-3px",
                })
                .appendTo(this.plot_div);

        d3.select(this.svg)
            .attr("preserveAspectRatio", "xMidYMin meet")
            .attr("viewBox", `0 0 ${nativeSize.width} ${nativeSize.height}`);

        ReactDOM.render(<VisualToolbar svg={this.svg} nativeSize={nativeSize} />, div[0]);
    }

    build_plot() {
        const {styles, arrow_styles} = this.store.settings;
        this.MAX_WIDTH = 300; // box dimensions
        this.MIN_HEIGHT = 100;
        this.SPACING_V = 100; // distance between boxes
        this.SPACING_H = 120;
        this.TEXT_OFFSET_X = 10;
        this.TEXT_OFFSET_Y = 20;
        this.TEXT_SIZE = 1;
        this.STYLE_DEFAULT = {
            x: "0", // +- centered around current box position (moves relevant text as well)
            y: "0",
            width: "0", // non-0 value for fixed
            height: "0",
            "spacing-horizontal": this.SPACING_H,
            "spacing-vertical": this.SPACING_V,
            "text-padding-x": "0", // +- centered around global text offset values
            "text-padding-y": "0",
            "text-color": "black",
            "text-style": "normal", // or "bold"
            "text-size": "0", // always appends "em" unit, +- centered around global text size
            "bg-color": "white",
            stroke: styles.stroke_color, // box border color
            "stroke-width": styles.stroke_width, // box border width
            rx: styles.stroke_radius, // box rounded edge horizontal
            ry: styles.stroke_radius, // box rounded edge vertical
            "arrow-color": arrow_styles["stroke_color"],
            "arrow-width": arrow_styles["stroke_width"],
            "arrow-type": arrow_styles["arrow_type"],
            "arrow-force-vertical": arrow_styles["force_vertical"],
        };

        this.plot_div.empty();
        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "A PRISMA diagram.")
            .attr("class", "d3")
            .attr("id", "svg-root")
            .node();
        this.cardrowlength = -1;

        const diagramSections = this.store.sections,
            connections = this.store.getConnections();

        // parse data structure
        let parent, child, sibling;
        for (let section of diagramSections) {
            let blockId = section.key,
                blockBoxInfo = section.label,
                sectionStyle = section.styling ?? {};

            if (!parent) {
                let initialNode = this.createRectangleWithText(
                    blockId,
                    blockBoxInfo,
                    WORKSPACE_START_X,
                    WORKSPACE_START_Y,
                    sectionStyle
                );
                parent = this.addNodeToHTML(initialNode);
            } else {
                parent = this.createNewVerticalNode(
                    parent,
                    blockId,
                    blockBoxInfo,
                    false,
                    sectionStyle
                );
            }
            if (section.block_layout) {
                this.drawBox(blockId, section);
                this.resizeNodes(parent);
                continue;
            }
            for (let i = 0; i < section.blocks.length; i++) {
                let box = section.blocks[i],
                    id = box.key,
                    boxInfo = `${box.label}: ${box.value}`,
                    blockStyle = box.styling ?? {};

                if (i > 0) {
                    let previous = sibling || child;
                    sibling = this.createNewHorizontalNode(previous, id, boxInfo, true, blockStyle);
                } else {
                    child = this.createChildNode(parent, id, boxInfo, blockStyle);
                    sibling = undefined;
                }

                if (box.sub_blocks) {
                    this.drawBox(id, box);
                }
            }
            this.resizeNodes(parent);
        }

        this.applyPostStyling();
        connections.forEach(connection => {
            this.drawConnection(connection);
        });
        this.setOverallDimensions(diagramSections);
        this.addResizeAndToolbar();
    }

    applyPostStyling() {
        // styling applied after the diagram is draw but before arrows are calculated
        // general box position, text-padding-y
        let allNodes = document.getElementsByClassName("node");
        for (let node of allNodes) {
            node = getGroup(node.id);

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

    setOverallDimensions(sections) {
        if (sections.length === 0) {
            this.w = 10;
            this.h = 10;
            return;
        }
        const bbs = sections.map(section =>
                d3
                    .select(document.getElementById(section.key))
                    .node()
                    .getBBox()
            ),
            hPadding = Math.max(sections.length - 1, 0) * this.SPACING_H;
        this.w = _.max(bbs.map(bb => bb.width));
        this.h = _.sum(bbs.map(bb => bb.height)) + hPadding;
    }
}

export default PrismaPlot;
