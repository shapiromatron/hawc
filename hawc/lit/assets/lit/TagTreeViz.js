import $ from '$';
import d3 from 'd3';

import D3Plot from 'utils/D3Plot';
import HAWCModal from 'utils/HAWCModal';

import ReferencesViewer from './ReferencesViewer';

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
        this.plot_div.html('');
        this.get_plot_sizes();
        this.build_plot_skeleton(false);
        this.draw_visualization();
        this.add_menu();
        this.trigger_resize();
    }

    get_plot_sizes() {
        var menu_spacing = this.options.show_menu_bar ? 40 : 0;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + 'px',
        });
    }

    set_defaults() {
        this.padding = { top: 40, right: 5, bottom: 5, left: 115 };
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

        let { x, y, width, height } = this.svg.viewBox.baseVal,
            increment = Math.ceil(-(this.w - value - this.path_length) / this.path_length);
        width = this.w + this.padding.left + this.padding.right + this.path_length * increment;
        this.svg.setAttribute('viewBox', `${x} ${y} ${width} ${height}`);
    }

    draw_visualization() {
        var i = 0,
            root = this.tagtree,
            vis = this.vis,
            tree = d3.layout.tree().size([this.h, this.w]),
            diagonal = d3.svg.diagonal().projection(function(d) {
                return [d.y, d.x];
            }),
            self = this;

        root.x0 = this.h / 2;
        root.y0 = 0;

        this.add_title();

        var radius_scale = d3.scale
            .pow()
            .exponent(0.5)
            .domain([0, root.data.reference_count])
            .range([this.minimum_radius, this.maximum_radius]);

        function toggleAll(d) {
            if (d.children) {
                d.children.forEach(toggleAll);
                toggle(d);
            }
        }

        function toggle(d) {
            if (d.children && d.children.length > 0) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
        }

        root.children.forEach(toggleAll);
        update(root);

        function fetch_references(nested_tag) {
            var title = '<h4>{0}</h4>'.printf(nested_tag.data.name),
                div = $('<div id="references_div"></div'),
                options = { tag: nested_tag, download_url: self.downloadURL },
                refviewer = new ReferencesViewer(div, options);

            self.modal
                .addHeader(title)
                .addBody(div)
                .addFooter('')
                .show({ maxWidth: 800 });
            nested_tag.get_reference_objects_by_tag(refviewer);
        }

        function update(source) {
            var duration = d3.event && d3.event.altKey ? 5000 : 500;

            // Compute the new tree layout.
            var nodes = tree.nodes(root).reverse();

            // Normalize for fixed-depth.
            nodes.forEach(function(d) {
                d.y = d.depth * self.path_length;
            });

            // Update the nodes…
            var node = vis.selectAll('g.tagnode').data(nodes, function(d) {
                return d.id || (d.id = ++i);
            });

            // Enter any new nodes at the parent's previous position.
            var nodeEnter = node
                .enter()
                .append('svg:g')
                .attr('class', 'tagnode')
                .attr('transform', (d) => `translate(${source.y0},${source.x0})`)
                .on('click', function(d) {
                    if (d3.event.ctrlKey || d3.event.metaKey) {
                        if (d.depth == 0) {
                            alert('Cannot view details on root-node.');
                        } else {
                            fetch_references(d);
                        }
                    } else {
                        toggle(d);
                        update(d);
                    }
                });

            nodeEnter
                .append('svg:circle')
                .attr('r', 1e-6)
                .style('fill', function(d) {
                    return d._children ? 'lightsteelblue' : '#fff';
                });

            nodeEnter
                .append('svg:text')
                .attr('x', 0)
                .attr('dy', function(d) {
                    return radius_scale(d.data.reference_count) + 15;
                })
                .attr('class', 'node_name')
                .attr('text-anchor', 'middle')
                .text(function(d) {
                    return d.data.name;
                })
                .style('fill-opacity', 1e-6);

            nodeEnter
                .append('svg:text')
                .attr('x', 0)
                .attr('dy', '3.5px')
                .attr('class', 'node_value')
                .attr('text-anchor', 'middle')
                .text(function(d) {
                    return d.data.reference_count;
                })
                .style('fill-opacity', 1e-6);

            // Transition nodes to their new position.
            var nodeUpdate = node
                .transition()
                .duration(duration)
                .attr('transform', (d) => `translate(${d.y},${d.x})`);

            nodeUpdate
                .select('circle')
                .attr('r', function(d) {
                    return radius_scale(d.data.reference_count);
                })
                .style('fill', function(d) {
                    return d._children ? 'lightsteelblue' : '#fff';
                });

            nodeUpdate.selectAll('text').style('fill-opacity', 1);

            // Transition exiting nodes to the parent's new position.
            var nodeExit = node
                .exit()
                .transition()
                .duration(duration)
                .attr('transform', (d) => `translate(${source.y},${source.x})`)
                .remove();

            nodeExit.select('circle').attr('r', 1e-6);

            nodeExit.select('text').style('fill-opacity', 1e-6);

            // Update the links…
            var link = vis.selectAll('path.tagslink').data(tree.links(nodes), function(d) {
                return d.target.id;
            });

            // Enter any new links at the parent's previous position.
            link
                .enter()
                .insert('svg:path', 'g')
                .attr('class', 'tagslink')
                .attr('d', function(d) {
                    self.check_svg_fit(source.y0);
                    var o = { x: source.x0, y: source.y0 };
                    return diagonal({ source: o, target: o });
                })
                .transition()
                .duration(duration)
                .attr('d', diagonal);

            // Transition links to their new position.
            link
                .transition()
                .duration(duration)
                .attr('d', diagonal);

            // Transition exiting nodes to the parent's new position.
            link
                .exit()
                .transition()
                .duration(duration)
                .attr('d', function(d) {
                    self.check_svg_fit(source.y);
                    var o = { x: source.x, y: source.y };
                    return diagonal({ source: o, target: o });
                })
                .remove();

            // Stash the old positions for transition.
            nodes.forEach(function(d) {
                d.x0 = d.x;
                d.y0 = d.y;
            });
        }
    }
}

export default TagTreeViz;
