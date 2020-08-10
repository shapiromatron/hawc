import $ from "$";
import * as d3 from "d3";

import D3Plot from "utils/D3Plot";
import HAWCModal from "utils/HAWCModal";
import HAWCUtils from "utils/HAWCUtils";

import ReferencesViewer from "./ReferencesViewer";

class TagTreeViz extends D3Plot {
    constructor(tagtree, plot_div, title, downloadURL, options) {
        // Displays multiple-dose-response details on the same view and allows for
        // custom visualization of these plots
        super();
        this.options = options || {};
        this.set_defaults();
        this.plot_div = $(plot_div);
        this.tagtree = tagtree;
        this.title_str = title;
        this.downloadURL = downloadURL;
        this.modal = new HAWCModal();
        if (this.options.build_plot_startup) {
            this.build_plot();
        }
    }

    build_plot() {
        this.plot_div.html("");
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.draw_visualization();
        this.add_menu();
        this.trigger_resize();
    }

    get_plot_sizes() {
        var menu_spacing = this.options.show_menu_bar ? 40 : 0;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + "px",
        });
    }

    set_defaults() {
        this.padding = {top: 40, right: 5, bottom: 5, left: 115};
        this.w = 1280 - this.padding.left - this.padding.right;
        this.h = 800 - this.padding.top - this.padding.bottom;
        this.path_length = 180;
        this.minimum_radius = 8;
        this.maximum_radius = 30;
        if (!this.options.build_plot_startup) {
            this.options.build_plot_startup = true;
        }
    }

    check_svg_fit(value) {
        // Ensure that the viewBox encapsulates the entire displayed chart.
        // It's possible multiple nodes may call this function at the same time,
        // so we check for how many path_lengths, rounded up, the graph extends
        // past the viewBox and set the viewBox.width to the graph width +
        // additional path_lengths.

        let {x, y, width, height} = this.svg.viewBox.baseVal,
            increment = Math.ceil(-(this.w - value - this.path_length) / this.path_length);
        width = this.w + this.padding.left + this.padding.right + this.path_length * increment;
        this.svg.setAttribute("viewBox", `${x} ${y} ${width} ${height}`);
    }

    draw_visualization() {
        var i = 0,
            vis = this.vis,
            diagonal = d3
                .linkHorizontal()
                .x(d => d.y)
                .y(d => d.x),
            self = this,
            buildVizDatasetNode = function(nestedTag) {
                return {
                    id: nestedTag.data.pk,
                    name: nestedTag.data.name,
                    depth: nestedTag.depth,
                    nestedTag,
                    numReferences: nestedTag.references.size,
                    numReferencesDeep: nestedTag.get_references_deep().length,
                    hasChildren: nestedTag.children.length > 0,
                    children: nestedTag.children.map(buildVizDatasetNode),
                };
            },
            rootNode = buildVizDatasetNode(this.tagtree.rootNode),
            tree = d3.tree().size([this.h, this.w]),
            treeNode = tree(d3.hierarchy(rootNode)),
            toggle = function toggle(d) {
                if (d.children && d.children.length > 0) {
                    d._children = d.children;
                    d.children = null;
                } else {
                    d.children = d._children;
                    d._children = null;
                }
            },
            toggleAll = function(d) {
                if (d.children) {
                    d.children.forEach(toggleAll);
                }
                toggle(d);
            },
            fetch_references = function(tag) {
                var title = `<h4>${tag.data.name}</h4>`,
                    div = $('<div id="references_div"></div'),
                    options = {tag, download_url: self.downloadURL},
                    refviewer = new ReferencesViewer(div, options);

                self.modal
                    .addHeader(title)
                    .addBody(div)
                    .addFooter("")
                    .show({maxWidth: 1200});
                tag.get_reference_objects_by_tag(refviewer, {filteredSubset: true});
            },
            update = function(source) {
                var duration = d3.event && d3.event.altKey ? 5000 : 500,
                    t = d3.transition().duration(duration);

                // Compute the new tree layout.
                treeNode = tree(treeNode);
                var nodes = treeNode.descendants().reverse();

                // Normalize for fixed-depth.
                nodes.forEach(d => (d.y = d.depth * self.path_length));

                // Update nodes
                var node = vis
                    .selectAll("g.tagnode")
                    .data(nodes, d => d.data.id || (d.data.id = ++i));

                // Enter any new nodes at the parent's previous position.
                var nodeEnter = node
                    .enter()
                    .append("svg:g")
                    .attr("class", "tagnode")
                    .attr("transform", () => `translate(${source.y0},${source.x0})`)
                    .on("click", function(d) {
                        if (d3.event.ctrlKey || d3.event.metaKey) {
                            if (d.depth == 0) {
                                alert("Cannot view details on root-node.");
                            } else {
                                fetch_references(d.data.nestedTag);
                            }
                        } else {
                            toggle(d);
                            update(d);
                        }
                    });

                nodeEnter
                    .append("svg:circle")
                    .attr("r", 1e-6)
                    .style("fill", d => (d.data.hasChildren ? "lightsteelblue" : "white"));

                nodeEnter
                    .append("svg:text")
                    .attr("x", 0)
                    .attr("y", d => radius_scale(d.data.numReferencesDeep) + 12)
                    .attr("class", "node_name")
                    .attr("text-anchor", "middle")
                    .text(d => d.data.name)
                    .style("fill-opacity", 1e-6)
                    .each(function() {
                        HAWCUtils.wrapText(this, 150);
                    });

                nodeEnter
                    .append("svg:text")
                    .attr("x", 0)
                    .attr("dy", "3.5px")
                    .attr("class", "node_value")
                    .attr("text-anchor", "middle")
                    .text(d => d.data.numReferencesDeep)
                    .style("fill-opacity", 1e-6);

                // Transition nodes to their new position.
                var nodeUpdate = nodeEnter.merge(node);
                nodeUpdate.transition(t).attr("transform", d => `translate(${d.y},${d.x})`);

                nodeUpdate
                    .selectAll("circle")
                    .transition(t)
                    .attr("r", d => radius_scale(d.data.numReferencesDeep))
                    .style("fill", d => (d.data.hasChildren ? "lightsteelblue" : "white"));

                nodeUpdate
                    .selectAll("text")
                    .transition(t)
                    .style("fill-opacity", 1);

                // Transition exiting nodes to the parent's new position.
                var nodeExit = node
                    .exit()
                    .transition()
                    .duration(duration)
                    .attr("transform", d => `translate(${source.y},${source.x})`)
                    .remove();

                nodeExit.select("circle").attr("r", 1e-6);

                nodeExit.select("text").style("fill-opacity", 1e-6);

                // Update links
                var link = vis
                    .selectAll("path.tagslink")
                    .data(treeNode.links(), d => d.target.data.id);

                // Enter any new links at the parent's previous position.
                link.enter()
                    .insert("svg:path", "g")
                    .attr("class", "tagslink")
                    .attr("d", function(d) {
                        self.check_svg_fit(source.y0);
                        var o = {x: source.x0, y: source.y0};
                        return diagonal({source: o, target: o});
                    })
                    .transition()
                    .duration(duration)
                    .attr("d", diagonal);

                // Transition links to their new position.
                link.transition()
                    .duration(duration)
                    .attr("d", diagonal);

                // Transition exiting nodes to the parent's new position.
                link.exit()
                    .transition()
                    .duration(duration)
                    .attr("d", function(d) {
                        self.check_svg_fit(source.y);
                        var o = {x: source.x, y: source.y};
                        return diagonal({source: o, target: o});
                    })
                    .remove();

                // Stash the old positions for transition.
                nodes.forEach(d => {
                    d.x0 = d.x;
                    d.y0 = d.y;
                });
            };

        this.add_title();
        treeNode.x0 = this.h / 2;
        treeNode.y0 = 0;

        var radius_scale = d3
            .scalePow()
            .exponent(0.5)
            .domain([0, treeNode.data.numReferencesDeep])
            .range([this.minimum_radius, this.maximum_radius]);

        treeNode.children.forEach(toggleAll);
        update(treeNode);
    }
}

export default TagTreeViz;
