import $ from '$';
import _ from 'lodash';

import BaseTable from 'utils/BaseTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';

import Exposure from './Exposure';
import Group from './Group';

class ComparisonSet {
    constructor(data) {
        this.data = data;
        this.groups = _.map(this.data.groups, function(d) {
            return new Group(d);
        });
        if (this.data.exposure) this.exposure = new Exposure(this.data.exposure);
    }

    static get_object(id, cb) {
        $.get('/epi/api/comparison-set/{0}/'.printf(id), function(d) {
            cb(new ComparisonSet(d));
        });
    }

    static displayFullPager($el, id) {
        ComparisonSet.get_object(id, function(d) {
            d.displayFullPager($el);
        });
    }

    static displayAsModal(id) {
        ComparisonSet.get_object(id, function(d) {
            d.displayAsModal();
        });
    }

    displayFullPager($el) {
        $el
            .hide()
            .append(this.build_details_div())
            .append(this.build_exposure_table())
            .append('<h2>Groups</h2>')
            .append(this.build_groups_table())
            .fadeIn();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">')
                .append(this.build_details_div())
                .append('<h2>Groups</h2>')
                .append(this.build_groups_table());

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({ maxWidth: 1000 });
    }

    build_breadcrumbs() {
        var urls;
        if (this.data.outcome) {
            urls = [
                {
                    url: this.data.outcome.study_population.study.url,
                    name: this.data.outcome.study_population.study.short_citation,
                },
                {
                    url: this.data.outcome.study_population.url,
                    name: this.data.outcome.study_population.name,
                },
                {
                    url: this.data.outcome.url,
                    name: this.data.outcome.name,
                },
            ];
        } else {
            urls = [
                {
                    url: this.data.study_population.study.url,
                    name: this.data.study_population.study.short_citation,
                },
                {
                    url: this.data.study_population.url,
                    name: this.data.study_population.name,
                },
            ];
        }
        urls.push({
            url: this.data.url,
            name: this.data.name,
        });
        return HAWCUtils.build_breadcrumbs(urls);
    }

    build_details_div() {
        return this.data.description ? $('<div>').html(this.data.description) : null;
    }

    build_exposure_table() {
        if (this.exposure === undefined) return;
        return $('<div>')
            .append('<h2>Exposure details</h2>')
            .append(this.exposure.build_details_table(true));
    }

    build_groups_table() {
        var tbl = new BaseTable(),
            colgroups = [25, 75];

        tbl.setColGroup(colgroups);

        _.each(this.groups, function(d) {
            tbl.addRow(d.build_tr());
        });

        return tbl.getTbl();
    }

    isEqual(other) {
        return other.data.id === this.data.id;
    }

    build_link() {
        return '<a href="{0}">{1}</a>'.printf(this.data.url, this.data.name);
    }
}

export default ComparisonSet;
