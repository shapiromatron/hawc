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
                url = null;
            if (tagtree.rootNode.data.name.startsWith("assessment-")) {
                // if this is an assessment-root node; hide the name
                tagtree.rename_top_level_node("");
            }
            tagtree.add_references(data[1]);
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
