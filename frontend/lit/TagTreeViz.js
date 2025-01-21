import * as d3 from "d3";
import {action, computed, observable, toJS} from "mobx";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import D3Plot from "shared/utils/D3Plot";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import $ from "$";

@observer
class VizOptions extends Component {
    componentDidUpdate() {
        // D3Plot will only remake navbar if it hasn't been defined
        delete this.props.viz.menu_div;
        this.props.viz.build_plot();
    }
    render() {
        const key = this.props.store.rerenderKey;
        return (
            <p className="form-text text-muted" data-value={key}>
                Click a node to expand to view child-nodes. Ctrl-click or ⌘-click to view references
                associated with an node (except root-node). Hold shift to drag nodes to new
                positions; click a node after dragging to update layout.
            </p>
        );
    }
}
VizOptions.propTypes = {
    store: PropTypes.object.isRequired,
    viz: PropTypes.object.isRequired,
};

class VizState {
    @observable options = null;
    @observable legendPosition = {x: 25, y: 25};
    @observable nodeOffsets = {};

    constructor(options) {
        this.options = options;
    }
    @computed
    get rerenderKey() {
        const options = this.options,
            values = ["show_legend", "show_counts", "hide_empty_tag_nodes"].map(d => options[d]);
        return h.hashString(JSON.stringify(toJS(values)));
    }
    @action.bound toggleOption(key) {
        this.options[key] = !this.options[key];
    }
    @action.bound changeOption(key, value) {
        this.options[key] = value;
    }
    @action.bound updateLegendPosition(x, y) {
        this.legendPosition = {x, y};
    }
    @action.bound updateDragLocation(id, x, y) {
        this.nodeOffsets[id] = {x, y};
    }
}

class TagTreeViz extends D3Plot {
    constructor(tagtree, el, title, options) {
        // Displays multiple-dose-response details on the same view and allows for
        // custom visualization of these plots
        super();
        this.stateStore = new VizState(options);
        this.set_defaults();
        this.el = $(el);
        this.plot_div = $("<div>").appendTo(el);
        this.options_div = $("<div>").appendTo(el);
        this.tagtree = tagtree;
        this.title_str = title;
        this.modal = new HAWCModal();
        this.build_plot();
        this.build_options();
    }

    build_plot() {
        this.plot_div.html("");
        this.build_plot_skeleton(false, "A dendrogram of reference counts for each tag");
        this.prepare_data();
        this.draw_visualization();
        this.add_menu();
        this._add_configuration();
        this.trigger_resize();
    }

    _add_configuration() {
        const {toggleOption, options} = this.stateStore,
            addToggle = (field, value, string) => {
                {
                    const text = (value ? "Hide" : "Show") + " " + string;
                    return $(`<button class="dropdown-item">${text}</button>`).on("click", () =>
                        toggleOption(field)
                    );
                }
            },
            group = $('<div class="dropdown btn-group">').append(
                $(
                    '<button class="btn btn-sm dropdown-toggle" data-toggle="dropdown">Options</button>'
                ).append(
                    $('<div class="dropdown-menu dropdown-menu-right">').append(
                        addToggle(
                            "hide_empty_tag_nodes",
                            !options.hide_empty_tag_nodes,
                            "tags with no references"
                        ),
                        addToggle("show_legend", options.show_legend, "legend"),
                        addToggle("show_counts", options.show_counts, "counts")
                    )
                )
            );
        this.menu_div.append(group);
    }

    build_options() {
        ReactDOM.render(<VizOptions viz={this} store={this.stateStore} />, this.options_div.get(0));
    }

    set_defaults() {
        const {width, height} = this.stateStore.options;
        this.padding = {top: 40, right: 5, bottom: 5, left: 115};
        this.w = width - this.padding.left - this.padding.right;
        this.h = height - this.padding.top - this.padding.bottom;
        this.path_length = 180;
        this.minimum_radius = 8;
        this.maximum_radius = 30;
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

    prepare_data() {
        // toggle reference pruning
        this.tagtree.prune_no_references(this.stateStore.options.hide_empty_tag_nodes);
    }

    draw_visualization() {
        var {nodeOffsets, options} = this.stateStore,
            store = this.stateStore,
            i = 0,
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
                const url = `/lit/assessment/${tag.assessment_id}/references/?tag_id=${tag.data.pk}`,
                    title = `<h3>References tagged: <a class="refTag mb-0" href="${url}">${tag.data.name}</a></h3>`,
                    div = $("<div>");

                self.modal
                    .addHeader(title)
                    .addBody(div)
                    .addFooter("")
                    .show({maxWidth: 1200});

                tag.renderPaginatedReferenceList(
                    div.get(0),
                    self.stateStore.options.can_edit,
                    self.stateStore.options.required_tags,
                    self.stateStore.options.pruned_tags
                );
            },
            update = function(event, source) {
                var duration = event && event.altKey ? 5000 : 500,
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
                    .on("click", function(event, d) {
                        if (event.ctrlKey || event.metaKey) {
                            fetch_references(d.data.nestedTag);
                        } else {
                            toggle(d);
                            update(event, d);
                        }
                    })
                    .call(
                        HAWCUtils.updateDragLocationTransform(
                            function(x, y) {
                                var p = d3.select(this),
                                    id = p.data()[0].data.id;
                                store.updateDragLocation(id, x, y);
                            },
                            {shift: true}
                        )
                    );

                nodeEnter
                    .append("svg:circle")
                    .attr("r", 1e-6)
                    .style("fill", d => (d.data.hasChildren ? "lightsteelblue" : "white"))
                    .append("svg:title")
                    .text("Ctrl-click or ⌘-click to view references");

                nodeEnter
                    .append("svg:text")
                    .attr("x", 0)
                    .attr("y", d => radius_scale(d.data.numReferencesDeep) + 12)
                    .attr("class", "node_name")
                    .attr("text-anchor", "middle")
                    .text(d => d.data.name)
                    .style("fill-opacity", 1e-6)
                    .each(function() {
                        HAWCUtils.wrapText(this, 170);
                    });

                if (options.show_counts) {
                    nodeEnter
                        .append("svg:text")
                        .attr("x", 0)
                        .attr("dy", "3.5px")
                        .attr("class", "node_value")
                        .attr("text-anchor", "middle")
                        .text(d => d.data.numReferencesDeep)
                        .style("fill-opacity", 1e-6);
                }

                // Transition nodes to their new position.
                var nodeUpdate = nodeEnter.merge(node);
                nodeUpdate.transition(t).attr("transform", d => {
                    const override = nodeOffsets[d.data.id];
                    if (override) {
                        d.x = override.y;
                        d.y = override.x;
                    }
                    return `translate(${d.y},${d.x})`;
                });

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
        this.title.style("cursor", "pointer").call(HAWCUtils.updateDragLocationXY(h.noop));
        if (options.show_legend) {
            this.add_legend();
        }
        treeNode.x0 = this.h / 2;
        treeNode.y0 = 0;

        var radius_scale = d3
            .scalePow()
            .exponent(0.5)
            .domain([0, treeNode.data.numReferencesDeep])
            .range(
                options.show_counts
                    ? [this.minimum_radius, this.maximum_radius]
                    : [
                          d3.mean([this.maximum_radius, this.minimum_radius]),
                          d3.mean([this.maximum_radius, this.minimum_radius]),
                      ]
            );

        treeNode.children.forEach(toggleAll);
        update(null, treeNode);
    }

    add_legend() {
        // create a new g.legend_group object on the main svg graphic
        const store = this.stateStore,
            legendPosition = store.legendPosition,
            buff = 5,
            data = [
                {fill: "lightsteelblue", text: "Has additional sub-tagging"},
                {fill: "white", text: "No additional sub-tagging"},
            ];

        const g = d3
            .select(this.svg)
            .append("g")
            .attr("transform", `translate(${legendPosition.x}, ${legendPosition.y})`)
            .attr("cursor", "pointer")
            .call(HAWCUtils.updateDragLocationTransform(store.updateLegendPosition));

        // Add color rectangles
        g.append("g")
            .attr("class", "tagnode")
            .selectAll("svg.circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", 10)
            .attr("cy", (d, i) => 10 + i * 25)
            .attr("r", 10)
            .style("fill", d => d.fill);

        // Add text label
        g.append("g")
            .selectAll("svg.text.labels")
            .data(data)
            .enter()
            .append("text")
            .attr("x", 25)
            .attr("y", (d, i) => 10 + i * 25)
            .attr("dy", "3.5px")
            .text(d => d.text);

        // // add bounding-rectangle around legend
        const dim = g.node().getBBox();
        g.insert("svg:rect", ":first-child")
            .attr("class", "legend")
            .attr("x", -buff)
            .attr("y", -buff)
            .attr("height", dim.height + 2 * buff)
            .attr("width", dim.width + 2 * buff);
    }
}

export default TagTreeViz;
