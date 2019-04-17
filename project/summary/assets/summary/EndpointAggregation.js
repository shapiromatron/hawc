import $ from '$';

import BaseTable from 'utils/BaseTable';
import HAWCModal from 'utils/HAWCModal';

import Endpoint from 'animal/Endpoint';
import EndpointDetailRow from 'animal/EndpointDetailRow';
import SmartTagContainer from 'smartTags/SmartTagContainer';

import EndpointAggregationExposureResponsePlot from './EndpointAggregationExposureResponsePlot';
import EndpointAggregationForestPlot from './EndpointAggregationForestPlot';
import BaseVisual from './BaseVisual';

class EndpointAggregation extends BaseVisual {
    constructor(data) {
        super(data);
        this.endpoints = data.endpoints.map(function(d) {
            var e = new Endpoint(d);
            e.switch_dose_units(data.dose_units);
            return e;
        });
        delete this.data.endpoints;
    }

    displayAsPage($el, options) {
        var title = $('<h1>').text(this.data.title),
            captionDiv = $('<div>').html(this.data.caption),
            caption = new SmartTagContainer(captionDiv),
            self = this;

        options = options || {};

        if (window.isEditable) title.append(this.addActionsMenu());

        this.$tblDiv = $('<div>');
        this.$plotDiv = $('<div>');

        $('<button type="button" class="btn btn-mini" title="Toggle table-view representation">')
            .append('<i class="icon-chevron-right"></i>')
            .click(function() {
                self.buildTbl();
            });

        $el
            .empty()
            .append(this.$plotDiv)
            .append(this.$tblDiv);

        if (!options.visualOnly) {
            $el
                .prepend(title)
                .append('<h2>Caption</h2>')
                .append(captionDiv);
        }

        this.buildTbl();
        this.plotData = this.getPlotData();
        this.buildPlot();
        caption.renderAndEnable();
        return this;
    }

    displayAsModal(options) {
        options = options || {};

        var self = this,
            modal = new HAWCModal(),
            captionDiv = $('<div>').html(this.data.caption),
            caption = new SmartTagContainer(captionDiv);

        this.$tblDiv = $('<div>');
        this.$plotDiv = $('<div>');

        modal.getModal().on('shown', function() {
            self.buildPlot();
            caption.renderAndEnable();
        });

        this.buildTbl();
        this.plotData = this.getPlotData();
        modal
            .addHeader($('<h4>').text(this.data.title))
            .addBody($('<div>').append(this.$plotDiv, this.$tblDiv, captionDiv))
            .addFooter('')
            .show({ maxWidth: 1200 });
    }

    buildTbl() {
        if (this.table) {
            this.table.unshift(this.table.pop());
        } else {
            // todo: get default from options, if one exists
            this.table = [this.buildTblPOD, this.buildTblEvidence];
        }
        this.$tblDiv.html(this.table[0].apply(this, arguments));
    }

    buildTblPOD() {
        var tbl = new BaseTable(),
            showEndpointDetail = function(e) {
                e.preventDefault();
                var tr = $(this)
                    .parent()
                    .parent();
                if (tr.data('detail_row')) {
                    tr.data('detail_row').toggle_view(!tr.data('detail_row').object_visible);
                } else {
                    var ep = tr.data('endpoint'),
                        div_id = String.random_string(),
                        colspan = tr.children().length;

                    tr
                        .after(
                            '<tr><td colspan="{0}"><div id="{1}"></div></td></tr>'.printf(
                                colspan,
                                div_id
                            )
                        )
                        .data('detail_row', new EndpointDetailRow(ep, '#' + div_id, 1));
                }
            };

        tbl.addHeaderRow([
            'Study',
            'Experiment',
            'Animal Group',
            'Endpoint',
            this.endpoints[0].data.noel_names.noel,
            this.endpoints[0].data.noel_names.loel,
            'BMD',
            'BMDL',
        ]);

        this.endpoints.forEach(function(e) {
            tbl
                .addRow([
                    '<a href="{0}">{1}</a>'.printf(
                        e.data.animal_group.experiment.study.url,
                        e.data.animal_group.experiment.study.short_citation
                    ),
                    '<a href="{0}">{1}</a>'.printf(
                        e.data.animal_group.experiment.url,
                        e.data.animal_group.experiment.name
                    ),
                    '<a href="{0}">{1}</a>'.printf(
                        e.data.animal_group.url,
                        e.data.animal_group.name
                    ),
                    e._endpoint_detail_td(),
                    e.get_special_dose_text('NOEL'),
                    e.get_special_dose_text('LOEL'),
                    e.get_bmd_special_values('BMD'),
                    e.get_bmd_special_values('BMDL'),
                ])
                .data('endpoint', e);
        });

        return tbl.getTbl().on('click', '.endpoint-selector', showEndpointDetail);
    }

    buildTblEvidence() {
        var tbl = new BaseTable();

        tbl.addHeaderRow(['Study', 'Experiment', 'Animal Group', 'Endpoint']);

        this.endpoints.forEach(function(e) {
            var ep_tbl = $('<div>')
                .append('<a href="{0}">{1}</a>'.printf(e.data.url, e.data.name))
                .append(e.build_endpoint_table($('<table class="table table-condensed">')));

            tbl.addRow([
                '<a href="{0}">{1}</a>'.printf(
                    e.data.animal_group.experiment.study.url,
                    e.data.animal_group.experiment.study.short_citation
                ),
                '<a href="{0}">{1}</a>'.printf(
                    e.data.animal_group.experiment.url,
                    e.data.animal_group.experiment.name
                ),
                '<a href="{0}">{1}</a>'.printf(e.data.animal_group.url, e.data.animal_group.name),
                ep_tbl,
            ]);
        });

        return tbl.getTbl();
    }

    buildPlot() {
        if (this.plot) {
            this.plot.unshift(this.plot.pop());
        } else {
            // todo: get default from options, if one exists
            this.plot = [
                new EndpointAggregationExposureResponsePlot(this, this.plotData),
                new EndpointAggregationForestPlot(this, this.plotData),
            ];
        }
        this.$tblDiv.html(this.plot[0].render(this.$plotDiv));
    }

    getPlotData() {
        return {
            title: this.data.title,
            endpoints: this.endpoints,
        };
    }

    addPlotToggleButton() {
        return {
            id: 'plot_toggle',
            cls: 'btn btn-mini',
            title: 'View alternate visualizations',
            text: '',
            icon: 'icon-circle-arrow-right',
            on_click: this.buildPlot.bind(this),
        };
    }
}

export default EndpointAggregation;
