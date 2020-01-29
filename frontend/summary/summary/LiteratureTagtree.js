import SmartTagContainer from "assets/smartTags/SmartTagContainer";
import BaseVisual from "./BaseVisual";

class LiteratureTagtree extends BaseVisual {
    constructor(data) {
        super(data);
    }

    getPlotData() {
        const urls = [
                `/lit/api/assessment/${this.data.assessment}/tags/`,
                `/lit/api/assessment/${this.data.assessment}/reference-tags/`,
            ],
            allRequests = urls.map(url => fetch(url).then(resp => resp.json()));

        Promise.all(allRequests).then(data => {
            console.log(data);
        });
    }

    displayAsPage($el, options) {
        var title = $("<h1>").text(this.data.title),
            captionDiv = $("<div>").html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $("<div>"),
            data = this.getPlotData();

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend(title).append(captionDiv);

        // new RoBHeatmapPlot(this, data, options).render($plotDiv);
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
