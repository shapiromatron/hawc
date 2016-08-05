import $ from '$';
import _ from 'underscore';

import HAWCModal from 'utils/HAWCModal';
import SmartTagContainer from 'smartTags/SmartTagContainer';

import RoBHeatmapPlot from './RoBHeatmapPlot';
import BaseVisual from './BaseVisual';


class RoBHeatmap extends BaseVisual {

    constructor(data){
        super(data);
        var studies = _.map(data.studies, function(d){
            return new window.app.study.Study(d);
        });
        this.roba = new window.app.riskofbias.Aggregation(studies);
        delete this.data.studies;
    }

    displayAsPage($el, options){
        var title = $('<h1>').text(this.data.title),
            caption = new SmartTagContainer($('<div>').html(this.data.caption)),
            $plotDiv = $('<div>'),
            data = this.getPlotData();

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        $el.empty().append($plotDiv);
        if (!options.visualOnly) $el.prepend(title).append(caption.getEl());

        new RoBHeatmapPlot(this, data, options).render($plotDiv);
        caption.ready();
        return this;
    }

    displayAsModal(options){
        options = options || {};

        var self = this,
            data = this.getPlotData(),
            caption = new SmartTagContainer($('<div>').html(this.data.caption)),
            $plotDiv = $('<div>'),
            modal = new HAWCModal();

        modal.getModal().on('shown', function(){
            new RoBHeatmapPlot(self, data, options).render($plotDiv);
            caption.ready();
        });

        modal.addHeader($('<h4>').text(this.data.title))
            .addBody([$plotDiv, caption.getEl()])
            .addFooter('')
            .show({maxWidth: 1200});
    }

    getPlotData(){
        return {
            aggregation: this.roba,
            settings: this.data.settings,
        };
    }

}

export default RoBHeatmap;
