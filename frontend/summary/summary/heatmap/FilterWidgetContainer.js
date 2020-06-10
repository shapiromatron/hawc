import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

const temp = function() {
    // Create blacklist container
    this.blacklist_container = this.svg_blacklist_container
        .insert("div", ":first-child")
        .attr("class", "exp_heatmap_container")
        .style("width", "20%")
        .style(
            "height",
            `${$(this.svg)
                .parent()
                .height()}px`
        )
        .style("vertical-align", "top")
        .style("display", "inline-block")
        .style("overflow", "auto");

    // Have resize trigger also resize blacklist container
    let old_trigger = this.trigger_resize;
    this.trigger_resize = forceResize => {
        old_trigger(forceResize);
        this.blacklist_container.style(
            "height",
            `${$(this.svg)
                .parent()
                .height()}px`
        );
    };
    $(window).resize(this.trigger_resize);

    let self = this,
        blacklist_select = this.blacklist_container.append("div").attr("class", "btn-group"),
        blacklist_input = this.blacklist_container.append("div"),
        blacklist_enter = blacklist_input
            .selectAll("input")
            .data(this.blacklist_domain)
            .enter()
            .append("div"),
        blacklist_label = blacklist_enter.append("label"),
        detail_handler = d => {
            this.modal
                .addHeader(`<h4>${d}</h4>`)
                .addFooter("")
                .show();
        };

    // Button to check all boxes
    blacklist_select
        .append("button")
        .attr("class", "btn")
        .text("All")
        .on("click", () => {
            blacklist_input.selectAll("label").each(function() {
                d3.select(this)
                    .select("input")
                    .property("checked", true);
            });
            blacklist_input.node().dispatchEvent(new Event("change"));
        });
    // Button to uncheck all boxes
    blacklist_select
        .append("button")
        .attr("class", "btn")
        .text("None")
        .on("click", () => {
            blacklist_input.selectAll("label").each(function() {
                d3.select(this)
                    .select("input")
                    .property("checked", false);
            });
            blacklist_input.node().dispatchEvent(new Event("change"));
        });

    // Before each label is a detail button
    blacklist_enter
        .insert("button", ":first-child")
        .attr("class", "btn btn-mini pull-left")
        .on("click", detail_handler)
        .html("<i class='icon-eye-open'></i>");

    // Each label has a checkbox and the value of the blacklisted item
    blacklist_label
        .append("input")
        .attr("type", "checkbox")
        .property("checked", true);
    blacklist_label.append("span").text(d => d);
    blacklist_input.on("change", function() {
        self.blacklist = [];
        d3.select(this)
            .selectAll("label")
            .each(function(d) {
                if (
                    !d3
                        .select(this)
                        .select("input")
                        .property("checked")
                )
                    self.blacklist.push(d);
            });
        self.filter_dataset();
        self.update_plot();
    });
};

@observer
class FilterWidget extends Component {
    render() {
        return <div>{this.props.widget.column}</div>;
    }
}
FilterWidget.propTypes = {
    store: PropTypes.object,
    widget: PropTypes.object,
};

@observer
class FilterWidgetContainer extends Component {
    render() {
        const {store} = this.props,
            {filter_widgets} = this.props.store.settings;
        return (
            <div>
                {filter_widgets.map((widget, idx) => (
                    <FilterWidget key={idx} store={store} widget={widget} />
                ))}
            </div>
        );
    }
}
FilterWidgetContainer.propTypes = {
    store: PropTypes.object,
};

export default FilterWidgetContainer;
