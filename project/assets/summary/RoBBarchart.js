import $ from '$';

import HAWCModal from 'utils/HAWCModal';

import SmartTagContainer from 'smartTags/SmartTagContainer';

import RoBBarchartPlot from './RoBBarchartPlot';
import RoBHeatmap from './RoBHeatmap';
import Visual from './Visual';


class RoBBarchart extends Visual {

    constructor(data){
        RoBHeatmap.apply(this, arguments);
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

        new RoBBarchartPlot(this, data, options).render($plotDiv);
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
            new RoBBarchartPlot(self, data, options).render($plotDiv);
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

export default RoBBarchart;
