import $ from '$';
import _ from 'lodash';

import HAWCModal from 'utils/HAWCModal';
import SmartTagContainer from 'smartTags/SmartTagContainer';
import Study from 'study/Study';
import Aggregation from 'riskofbias/Aggregation';

import RoBHeatmapPlot from './RoBHeatmapPlot';
import BaseVisual from './BaseVisual';

class RoBHeatmap extends BaseVisual {
    constructor(data) {
        super(data);
        var studies = _.map(data.studies, function(d) {
            return new Study(d);
        });
        this.roba = new Aggregation(studies);
        delete this.data.studies;
    }

    displayAsPage($el, options) {
        var title = $('<h1>').text(this.data.title),
            captionDiv = $('<div>').html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $('<div>'),
            data = this.getPlotData();

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend(title).append(captionDiv);

        new RoBHeatmapPlot(this, data, options).render($plotDiv);
        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};

        var self = this,
            data = this.getPlotData(),
            captionDiv = $('<div>').html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            $plotDiv = $('<div>'),
            modal = new HAWCModal();

        modal.getModal().on('shown', function() {
            new RoBHeatmapPlot(self, data, options).render($plotDiv);
            caption.renderAndEnable();
        });

        modal
            .addHeader($('<h4>').text(this.data.title))
            .addBody([$plotDiv, captionDiv])
            .addFooter('')
            .show({ maxWidth: 1200 });
    }

    getPlotData() {
        return {
            aggregation: this.roba,
            settings: this.data.settings,
            assessment_rob_name: this.data.assessment_rob_name,
        };
    }
}

export default RoBHeatmap;
