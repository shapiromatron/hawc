import * as d3 from "d3";
import * as d3Arrow from "d3-arrow";
import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";
import VisualToolbar from "shared/components/VisualToolbar";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

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
    nodeOnClick = function(e, plot, refs) {
        e.stopPropagation();
        const detailEl = document.getElementById(`${plot.store.settingsHash}-detail-section`),
            formData = new FormData();
        detailEl.innerText = "Loading...";
        formData.append("ids", Array(...refs).join(","));
        // TODO: change detail header to the text of the clicked node
        fetch(plot.store.dataset.url, h.fetchPostForm(plot.store.getCsrfToken(), formData))
            .then(resp => resp.text())
            .then(html => (detailEl.innerHTML = html));
    },
    connectPoints = function(svg, STYLE_DEFAULT, id, xy1, xy2, arrowhead = true, styling = {}) {
        for (const [key, value] of Object.entries(STYLE_DEFAULT)) {
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
        d3.select(svg).call(arrow);
        d3.select(svg)
            .append("polyline")
            .attr("marker-end", `url(#${id})`)
            .attr("points", [xy1, xy2])
            .attr("stroke", styling["arrow-color"])
            .attr("stroke-width", styling["arrow-width"]);
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
        this.setDefaults();
        this.buildRootSvg();
        this.buildSections();
        this.applyPostStyling();
        this.buildConnections();
        this.setOverallDimensions();
        this.addResizeAndToolbar();
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

    addNodeToHTML(node, opts) {
        const parent = opts.parent,
            refs = opts.refs;

        if (parent) {
            document.getElementById(parent.id).append(node.group);
        } else {
            this.svg.append(node.group);
        }
        let txtEle = this.addTextToNode(node, node.id + "-text", node.text, node.styling),
            handleClick = e => {
                // only handle click events if references are passed
                if (refs) {
                    nodeOnClick(e, this, refs);
                }
            };
        node.text = txtEle;
        node.rect.onclick = handleClick;
        txtEle.onclick = handleClick;
        return node;
    }

    drawConnection(connection) {
        // https://github.com/HarryStevens/d3-arrow
        // https://observablehq.com/d/7759e56ba89ced03
        const id = connection.key,
            styling = _.clone(this.store.settings.styles),
            node1BBox = getGroup(connection.src).rect.getBBox(),
            node2BBox = getGroup(connection.dst).rect.getBBox(),
            svg = this.svg,
            DEF = this.STYLE_DEFAULT;

        // add overrides (TODO - this isn't working yet, to fix)
        if (connection.styling) {
            _.merge(styling, connection.styling);
        }

        let xMidpoint, yMidpoint, node1XY, node1Midpoint, node2Midpoint, node2XY;
        // same x = vertical
        if (node1BBox.x == node2BBox.x || styling["arrow-force-vertical"] == true) {
            yMidpoint = (node2BBox.y - (node1BBox.y + node1BBox.height)) / 2;
            yMidpoint = node1BBox.y + node1BBox.height + yMidpoint;
            node1XY = [node1BBox.x + node1BBox.width / 2, node1BBox.y + node1BBox.height];
            node1Midpoint = [node1BBox.x + node1BBox.width / 2, yMidpoint];
            node2Midpoint = [node2BBox.x + node2BBox.width / 2, yMidpoint];
            node2XY = [node2BBox.x + node2BBox.width / 2, node2BBox.y];
        } else {
            xMidpoint = (node2BBox.x - (node1BBox.x + node1BBox.width)) / 2;
            xMidpoint = node1BBox.x + node1BBox.width + xMidpoint;
            node1XY = [node1BBox.x + node1BBox.width, node1BBox.y + node1BBox.height / 2];
            node1Midpoint = [xMidpoint, node1BBox.y + node1BBox.height / 2];
            node2Midpoint = [xMidpoint, node2BBox.y + node2BBox.height / 2];
            node2XY = [node2BBox.x, node2BBox.y + node2BBox.height / 2];
        }
        connectPoints(svg, DEF, id + "_1", node1XY, node1Midpoint, false, styling);
        connectPoints(svg, DEF, id + "_2", node1Midpoint, node2Midpoint, false, styling);
        connectPoints(svg, DEF, id + "_3", node2Midpoint, node2XY, true, styling);
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
            return this.addNodeToHTML(verticalNode, {parent: prevNode.parent}); //add refs
        }
        return this.addNodeToHTML(verticalNode, {parent: undefined}); //add refs
    }

    createNewHorizontalNode(prevNode, id, text, group = false, styling = {}, opts = {}) {
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
        horizontalNode = this.addNodeToHTML(horizontalNode, {
            parent: prevNode.parent,
            refs: opts.refs,
        });

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

    createChildNode(parent, id, text, styling = {}, opts = {}) {
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

        return this.addNodeToHTML(child, {parent, refs: opts.refs}); //add refs
    }

    drawList(node, col) {
        // helper function for parsing the data structure
        // handles list/card layouts at the section and block level
        if (col.box_layout !== "list") {
            return;
        }

        _.each(col.items, (item, i) => {
            let blockStyle = {},
                subblockId = item.key,
                subblockText = `• ${item.label}: ${item.value}`;

            blockStyle["text-padding-x"] = blockStyle["text-padding-x"] || 5;

            let txtEle = this.addTextToNode(node, subblockId, subblockText, blockStyle);
            txtEle.onclick = e => {
                nodeOnClick(e, this, item.refs);
            };
        });
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

    buildRootSvg() {
        this.plot_div.empty();
        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "A PRISMA diagram.")
            .attr("class", "d3")
            .attr("id", "svg-root")
            .node();
    }

    buildSections() {
        const diagramSections = this.store.sections;
        let parent = null;
        _.each(diagramSections, section => {
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
                parent = this.addNodeToHTML(initialNode, {parent: undefined, refs: undefined});
            } else {
                parent = this.createNewVerticalNode(
                    parent,
                    blockId,
                    blockBoxInfo,
                    false,
                    sectionStyle
                );
            }
            this.drawBlocks(parent, section);
            this.resizeNodes(parent);
        });
    }

    drawBlocks(parent, section) {
        let node, lastHorizontalNode;
        _.each(section.blocks, (block, j) => {
            let id = block.key,
                boxInfo = `${block.label}: ${block.value}`,
                blockStyle = block.styling ?? {};

            if (j > 0) {
                node = this.createNewHorizontalNode(
                    lastHorizontalNode,
                    id,
                    boxInfo,
                    true,
                    blockStyle,
                    {refs: block.refs}
                );
                lastHorizontalNode = node;
            } else {
                node = this.createChildNode(parent, id, boxInfo, blockStyle, {refs: block.refs});
                lastHorizontalNode = node;
            }
            this.drawList(node, block);
        });
    }

    buildConnections() {
        this.store.getConnections().forEach(connection => {
            this.drawConnection(connection);
        });
    }

    setDefaults() {
        const {styles, arrow_styles} = this.store.settings;
        this.MAX_WIDTH = 300; // box dimensions
        this.MIN_HEIGHT = 100;
        this.SPACING_V = 100; // distance between boxes
        this.SPACING_H = 120;
        this.TEXT_OFFSET_X = 10;
        this.TEXT_OFFSET_Y = 20;
        this.TEXT_SIZE = 1.1;
        this.STYLE_DEFAULT = {
            x: "0", // +- centered around current box position (moves relevant text as well)
            y: "0",
            width: "0", // non-0 value for fixed
            height: "0",
            "spacing-horizontal": this.SPACING_H,
            "spacing-vertical": this.SPACING_V,
            "text-padding-x": styles.padding_x, // +- centered around global text offset values
            "text-padding-y": styles.padding_y,
            "text-color": styles.font_color,
            "text-style": "normal", // or "bold"
            "text-size": styles.font_size, // always appends "em" unit, +- centered around global text size
            "bg-color": styles.bg_color,
            stroke: styles.stroke_color, // box border color
            "stroke-width": styles.stroke_width, // box border width
            rx: styles.stroke_radius, // box rounded edge horizontal
            ry: styles.stroke_radius, // box rounded edge vertical
            "arrow-color": arrow_styles["stroke_color"],
            "arrow-width": arrow_styles["stroke_width"],
            "arrow-type": arrow_styles["arrow_type"],
            "arrow-force-vertical": arrow_styles["force_vertical"],
        };
        this.cardrowlength = -1;
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

    setOverallDimensions() {
        const {sections} = this.store;
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
