import $ from '$';

import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';

class Exposure {
    constructor(data) {
        this.data = data;
    }

    static get_object(id, cb) {
        $.get('/epi/api/exposure/{0}/'.printf(id), function(d) {
            cb(new Exposure(d));
        });
    }

    static displayAsModal(id) {
        Exposure.get_object(id, function(d) {
            d.displayAsModal();
        });
    }

    static displayFullPager($el, id) {
        Exposure.get_object(id, function(d) {
            d.displayFullPager($el);
        });
    }

    build_breadcrumbs() {
        var urls = [
            {
                url: this.data.study_population.study.url,
                name: this.data.study_population.study.short_citation,
            },
            {
                url: this.data.study_population.url,
                name: this.data.study_population.name,
            },
            {
                url: this.data.url,
                name: this.data.name,
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_exposure_li() {
        var lis = [];
        if (this.data.inhalation) lis.push('Inhalation');
        if (this.data.dermal) lis.push('Dermal');
        if (this.data.oral) lis.push('Oral');
        if (this.data.in_utero) lis.push('In utero');
        if (this.data.iv) lis.push('IV');
        if (this.data.unknown_route) lis.push('Unknown route');
        return lis;
    }

    build_central_tendencies_table() {
        var ctTable = $('<table/>').addClass('bordered');
        var ctHeaders = [
            'Estimate',
            'Estimate type',
            'Variance',
            'Variance type',
            'Lower Bound Interval',
            'Upper Bound Interval',
            'Lower CI',
            'Upper CI',
            'Lower Range',
            'Upper Range',
        ];

        var headerRow = $('<tr/>').appendTo(ctTable);
        for (var i = 0; i < ctHeaders.length; i++) {
            $('<th/>')
                .html(ctHeaders[i].replace(/ /g, '&nbsp'))
                .appendTo(headerRow);
        }

        this.data.central_tendencies.forEach(function(el, idx) {
            var row = $('<tr/>').appendTo(ctTable);
            for (var i = 0; i < ctHeaders.length; i++) {
                var val = el[ctHeaders[i].replace(/ /g, '_').toLowerCase()];
                if (val != null && typeof val == 'string') {
                    val = val.replace(/ /g, '&nbsp;');
                }
                $('<td/>')
                    .html(val)
                    .appendTo(row);
            }
        });
        return ctTable;
    }

    build_details_table(showLink) {
        var link = showLink === true ? this.build_link() : undefined;

        var ctTable = this.build_central_tendencies_table();

        return new DescriptiveTable()
            .add_tbody_tr('Name', link)
            .add_tbody_tr('What was measured', this.data.measured)
            .add_tbody_tr('Measurement metric', this.data.metric)
            .add_tbody_tr('Measurement metric units', this.data.metric_units.name)
            .add_tbody_tr('Measurement description', this.data.metric_description)
            .add_tbody_tr_list('Known exposure routes', this.get_exposure_li())
            .add_tbody_tr('Analytical method', this.data.analytical_method)
            .add_tbody_tr('Exposure description', this.data.exposure_description)
            .add_tbody_tr('Age of exposure', this.data.age_of_exposure)
            .add_tbody_tr('Duration', this.data.duration)
            .add_tbody_tr('Sampling period', this.data.sampling_period)
            .add_tbody_tr('Exposure distribution', this.data.exposure_distribution)
            .add_tbody_tr('Central tendencies', ctTable)
            .add_tbody_tr('Description', this.data.description)
            .get_tbl();
    }

    displayFullPager($el) {
        var tbl = this.build_details_table();
        $el
            .hide()
            .append(tbl)
            .fadeIn();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row-fluid">').append($details)
            );

        $details.append(this.build_details_table());

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({ maxWidth: 1000 });
    }

    build_link() {
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.name);
    }
}

export default Exposure;
