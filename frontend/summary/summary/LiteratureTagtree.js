import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";
import TagTree from "lit/TagTree";
import TagTreeViz from "lit/TagTreeViz";

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
            let tagtree = new TagTree(data[0]),
                title = "hi",
                url = "/url";
            tagtree.build_top_level_node("");
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

        var data = this.getPlotData(),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            modal = new HAWCModal();

        modal.getModal().on("shown", () => {
            // new RoBHeatmapPlot(self, data, options).render($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader($("<h4>").text(this.data.title))
            .addBody([$plotDiv, captionDiv])
            .addFooter("");
    }
}

export default LiteratureTagtree;
