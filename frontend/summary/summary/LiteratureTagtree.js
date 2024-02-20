import TagTree from "lit/TagTree";
import TagTreeViz from "lit/TagTreeViz";
import _ from "lodash";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import BaseVisual from "./BaseVisual";
import {handleVisualError} from "./common";

class LiteratureTagtree extends BaseVisual {
    constructor(data) {
        super(data);
    }

    buildPlot($plotDiv, data) {
        let tagtree = new TagTree(data[0][0], this.data.assessment, null),
            title = this.data.title;

        if (tagtree.rootNode.data.name.startsWith("assessment-")) {
            // if this is an assessment-root node; hide the name
            tagtree.rename_top_level_node(this.data.assessment_name);
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

        _.extend(this.data.settings, {can_edit: window.isEditable});

        new TagTreeViz(tagtree, $plotDiv, title, this.data.settings);
    }

    buildViz($plotDiv, data) {
        try {
            this.buildPlot($plotDiv, data);
        } catch (error) {
            handleVisualError(error, null);
        }
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
        var title = $("<h2>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>");

        options = options || {};

        const actions = window.isEditable ? this.addActionsMenu() : null;

        $el.empty().append($plotDiv);

        if (!options.visualOnly) {
            var headerRow = $('<div class="d-flex">').append([
                title,
                HAWCUtils.unpublished(this.data.published, window.isEditable),
                actions,
            ]);
            $el.prepend(headerRow).append(captionDiv);
        }

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

        modal.getModal().on("shown.bs.modal", () => {
            this.getPlotData($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader([
                $("<h4>").text(this.data.title),
                HAWCUtils.unpublished(this.data.published, window.isEditable),
            ])
            .addBody([$plotDiv, captionDiv])
            .addFooter("")
            .show({maxWidth: 1200});
    }
}

export default LiteratureTagtree;
