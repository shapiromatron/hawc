import $ from '$';
import d3 from 'd3';

import HAWCModal from 'utils/HAWCModal';

import SmartTagContainer from 'smartTags/SmartTagContainer';

import CrossviewPlot from './CrossviewPlot';
import EndpointAggregation from './EndpointAggregation';


class Crossview extends EndpointAggregation {

    constructor(data){
        super(data);
        // D3.js monkey-patch
        d3.selection.prototype.moveToFront = function(){
            return this.each(function(){
                this.parentNode.appendChild(this);
            });
        };
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

        new CrossviewPlot(this, data, options).render($plotDiv);
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
            new CrossviewPlot(self, data, options).render($plotDiv);
            caption.ready();
        });

        modal.addHeader($('<h4>').text(this.data.title))
            .addBody([$plotDiv, caption.getEl()])
            .addFooter('')
            .show({maxWidth: 1200});
    }

    getPlotData(){
        return {
            title: this.data.title,
            endpoints: this.endpoints,
            dose_units: this.data.dose_units,
            settings: this.data.settings,
        };
    }

}

export default Crossview;
