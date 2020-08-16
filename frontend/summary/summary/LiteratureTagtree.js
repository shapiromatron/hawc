import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import TagTree from "lit/TagTree";
import TagTreeViz from "lit/TagTreeViz";
import HAWCModal from "utils/HAWCModal";
import ReactDOM from "react-dom";
import React, {Component} from "react";
import PropTypes from "prop-types";

class Checkbox extends Component {
    render() {
        return (
            <div>
                <label htmlFor={this.props.id} className="checkbox">
                    {this.props.label}
                    <input
                        id={this.props.id}
                        type="checkbox"
                        defaultChecked={this.props.checked}
                        onChange={this.props.onChange}
                    />
                </label>
            </div>
        );
    }
}
Checkbox.propTypes = {
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    checked: PropTypes.bool.isRequired,
};

class LiteratureTagtree extends BaseVisual {
    constructor(data) {
        super(data);
    }

    buildCheckbox($plotDiv, onChange) {
        this.data.settings.hide_empty = Boolean(this.data.settings.hide_empty);
        let checkbox = $("<div></div>").insertBefore($plotDiv);
        ReactDOM.render(
            <Checkbox
                id="cb-hide-empty"
                label="Hide nodes without references"
                onChange={onChange}
                checked={this.data.settings.hide_empty}
            />,
            checkbox[0]
        );
    }

    buildPlot($plotDiv, data) {
        let tagtree = new TagTree(data[0][0], this.data.assessment, null),
            title = this.data.title,
            url = `/lit/assessment/${this.data.assessment}/references/download/`;

        if (tagtree.rootNode.data.name.startsWith("assessment-")) {
            // if this is an assessment-root node; hide the name
            tagtree.rename_top_level_node("");
        }

        /*
            Filter references displayed based on the presence of a reference containing a
            specific tag; for example, filter to only show references which have had tags
            123 and 456 applied.
            */
        let reference_tag_mapping = data[1];
        if (this.data.settings.required_tags.length > 0) {
            let required_tags = new Set(this.data.settings.required_tags),
                included_references = new Set();

            // find references which should be included
            reference_tag_mapping.forEach(row => {
                if (required_tags.has(row.tag_id)) {
                    included_references.add(row.reference_id);
                }
            });

            // filter mapping to only include these references
            reference_tag_mapping = reference_tag_mapping.filter(row =>
                included_references.has(row.reference_id)
            );
        }
        tagtree.add_references(reference_tag_mapping);

        // remove nodes from tagtree
        this.data.settings.pruned_tags.forEach(tagId => tagtree.prune_tree(tagId));

        // change root node
        tagtree.reset_root_node(this.data.settings.root_node);

        // prune nodes with no refs from root node
        if (this.data.settings.hide_empty) tagtree.prune_no_references();

        new TagTreeViz(tagtree, $plotDiv, title, url);
    }

    buildViz($plotDiv, data) {
        this.buildPlot($plotDiv, data);
        this.buildCheckbox($plotDiv, () => {
            this.data.settings.hide_empty = !this.data.settings.hide_empty;
            this.buildPlot($plotDiv, data);
        });
    }

    getPlotData($plotDiv) {
        const urls = [
                `/lit/api/tags/?assessment_id=${this.data.assessment}`,
                `/lit/api/assessment/${this.data.assessment}/reference-tags/`,
            ],
            allRequests = urls.map(url => fetch(url).then(resp => resp.json()));
        Promise.all(allRequests).then(data => {
            this.buildViz($plotDiv, data);
        });
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>");

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend(title).append(captionDiv);

        this.getPlotData($plotDiv);

        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};

        var captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal();

        modal.getModal().on("shown", () => {
            this.getPlotData($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader($("<h4>").text(this.data.title))
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }
}

export default LiteratureTagtree;
