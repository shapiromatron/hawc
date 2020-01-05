import $ from '$';
import _ from 'lodash';

import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';

import ComparisonSet from './ComparisonSet';
import Result from './Result';

class Outcome {
    constructor(data) {
        this.data = data;
        this.results = _.map(data.results, function(d) {
            return new Result(d);
        });
        this.comparison_sets = _.map(data.comparison_sets, function(d) {
            return new ComparisonSet(d);
        });
    }

    static get_object(id, cb) {
        $.get('/epi/api/outcome/{0}/'.printf(id), function(d) {
            cb(new Outcome(d));
        });
    }

    static displayAsModal(id) {
        Outcome.get_object(id, function(d) {
            d.displayAsModal();
        });
    }

    static displayFullPager($el, id) {
        Outcome.get_object(id, function(d) {
            d.displayFullPager($el);
        });
    }

    build_details_table() {
        return new DescriptiveTable()
            .add_tbody_tr('Name', this.data.name)
            .add_tbody_tr('System', this.data.system)
            .add_tbody_tr('Effect', this.data.effect)
            .add_tbody_tr('Effect subtype', this.data.effect_subtype)
            .add_tbody_tr_list('Effect tags', _.map(this.data.effects, 'name'))
            .add_tbody_tr('Diagnostic', this.data.diagnostic)
            .add_tbody_tr('Diagnostic description', this.data.diagnostic_description)
            .add_tbody_tr('Age of outcome measurement', this.data.age_of_measurement)
            .add_tbody_tr('Outcome N', this.data.outcome_n)
            .add_tbody_tr('Summary', this.data.summary)
            .get_tbl();
    }

    build_results_tabs() {
        var container = $('<div>').append('<h2>Results</h2>'),
            tabs = $('<ul class="nav nav-tabs">'),
            content = $('<div class="tab-content">');

        if (this.results.length === 0) {
            return container.append('<p class="help-block">No results are available.</p>');
        }

        _.each(this.results, function(d, i) {
            var isActive = i === 0;
            tabs.append(d.build_tab(isActive));
            content.append(d.build_content_tab(isActive));
        });

        container.on('shown', 'a[data-toggle="tab"]', function(e) {
            e.stopPropagation();
            $(this.getAttribute('href')).trigger('plotDivShown');
        });

        return container.append(tabs).append(content);
    }

    get_unused_comparison_sets() {
        // get comparison sets associated with no results
        var usedSets = _.map(this.results, 'comparison_set');
        return _.filter(this.comparison_sets, function(d2) {
            return !_.some(
                _.map(usedSets, function(d1) {
                    return d1.isEqual(d2);
                })
            );
        });
    }

    build_comparison_set_bullets() {
        if (this.data.can_create_sets) {
            var $el = $('<div>'),
                grps = this.get_unused_comparison_sets();
            $el.append('<h2>Unused comparison sets</h2>');
            if (grps.length > 0) {
                $el.append(
                    HAWCUtils.buildUL(grps, function(d) {
                        return '<li>{0}</li>'.printf(d.build_link());
                    })
                );
            } else {
                $el.append('<p class="help-block">No comparison sets are available.</p>');
            }
        }
        return $el;
    }

    buildListRow() {
        let link = `<a href="${this.data.url}" target="_blank">${this.data.name}</a>`,
            detail = $(
                '<i class="fa fa-eye eyeEndpointModal" title="quick view" style="display: none">'
            ).click(() => {
                this.displayAsModal({ complete: true });
            }),
            outcome = $('<span>')
                .append(link, detail)
                .hover(detail.fadeIn.bind(detail), detail.fadeOut.bind(detail));

        return [
            `<a href=${this.data.study_population.study.url} target="_blank">${
                this.data.study_population.study.short_citation
            }</a>`,
            `<a href=${this.data.study_population.url} target="_blank">${
                this.data.study_population.name
            }</a>`,
            outcome,
            this.data.system ? this.data.system : '--',
            this.data.effect ? this.data.effect : '--',
            this.data.diagnostic ? this.data.diagnostic : '--',
        ];
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

    displayFullPager($el) {
        $el
            .hide()
            .append(this.build_details_table())
            .append(this.build_results_tabs())
            .append(this.build_comparison_set_bullets())
            .fadeIn(this.triggerFirstTabShown.bind(this, $el));
    }

    displayAsModal() {
        var opts = { maxWidth: 1000 },
            modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $content = $('<div class="container-fluid">')
                .append(this.build_details_table())
                .append(this.build_results_tabs())
                .append(this.build_comparison_set_bullets());

        modal
            .addHeader(title)
            .addBody($content)
            .addFooter('')
            .show(opts, this.triggerFirstTabShown.bind(this, $content));
    }

    triggerFirstTabShown($el) {
        $el.find('.nav-tabs .active a').trigger('shown');
    }
}

export default Outcome;
