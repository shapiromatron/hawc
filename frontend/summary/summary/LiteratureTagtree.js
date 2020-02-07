import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import TagTree from "lit/TagTree";
import TagTreeViz from "lit/TagTreeViz";
import HAWCModal from "utils/HAWCModal";

class LiteratureTagtree extends BaseVisual {
    constructor(data) {
        super(data);
    }

    getPlotData($plotDiv) {
        const urls = [
                `/lit/api/tags/?assessment_id=${this.data.assessment}`,
                `/lit/api/assessment/${this.data.assessment}/reference-tags/`,
            ],
            allRequests = urls.map(url => fetch(url).then(resp => resp.json()));
        this.$plotDiv = $plotDiv;
        Promise.all(allRequests).then(data => {
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

            new TagTreeViz(tagtree, this.$plotDiv, title, url);
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
