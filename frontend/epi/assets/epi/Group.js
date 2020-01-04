import $ from '$';
import _ from 'lodash';

import BaseTable from 'utils/BaseTable';
import DescriptiveTable from 'utils/DescriptiveTable';
import HawcTooltip from 'utils/HawcTooltip';

import GroupDescription from './GroupDescription';

class Group {
    constructor(data) {
        this.data = data;
        this.descriptions = _.map(this.data.descriptions, function(d) {
            return new GroupDescription(d);
        });
    }

    static get_object(id, cb) {
        $.get('/epi/api/group/{0}/'.printf(id), function(d) {
            cb(new Group(d));
        });
    }

    static displayFullPager($el, id) {
        Group.get_object(id, function(d) {
            d.displayFullPager($el);
        });
    }

    displayFullPager($el) {
        $el.hide().append(this.build_details_table());

        if (this.descriptions.length > 0) {
            $el
                .append('<h2>Numerical group descriptions</h2>')
                .append(this.build_group_descriptions_table());
        }

        $el.fadeIn();
    }

    get_content() {
        var d = this.data,
            vals = [],
            addTuple = function(lbl, val) {
                if (val) vals.push([lbl, val]);
            };

        addTuple('Numerical value', d.numeric);
        addTuple('Comparative name', d.comparative_name);
        addTuple('Sex', d.sex);
        addTuple('Ethnicities', _.map(d.ethnicities, 'name'));
        addTuple('Eligible N', d.eligible_n);
        addTuple('Invited N', d.invited_n);
        addTuple('Participant N', d.participant_n);
        addTuple('Is control?', d.isControl);
        addTuple('Comments', d.comments);
        return vals;
    }

    build_tr() {
        var d = this.data,
            ul = $('<ul>'),
            url = $('<a>')
                .attr('href', d.url)
                .text(d.name),
            addLI = function(key, val) {
                if (val) {
                    ul.append('<li><strong>{0}:</strong> {1}</li>'.printf(key, val));
                }
            },
            content = this.get_content();

        _.each(content, function(d) {
            var val = d[1] instanceof Array ? d[1].join(', ') : d[1];
            addLI(d[0], val);
        });

        return [url, ul];
    }

    build_details_table() {
        var content = this.get_content(),
            tbl = new DescriptiveTable();

        _.each(content, function(d) {
            if (d[1] instanceof Array) {
                tbl.add_tbody_tr_list(d[0], d[1]);
            } else {
                tbl.add_tbody_tr(d[0], d[1]);
            }
        });

        return tbl.get_tbl();
    }

    build_group_descriptions_table() {
        var tbl = new BaseTable(),
            headers = ['Variable', 'Mean', 'Variance', 'Lower value', 'Upper value', 'Calculated'],
            colgroups = [25, 15, 15, 15, 15, 15]; // todo: number observations? - review data imports

        tbl.addHeaderRow(headers);
        tbl.setColGroup(colgroups);

        _.each(this.descriptions, function(d) {
            tbl.addRow(d.build_tr(tbl.footnotes));
        });

        return tbl.getTbl();
    }

    show_tooltip(e) {
        e.preventDefault();
        var opts = { width: '700px', height: '380px' },
            title = this.data.name,
            content = this.build_details_table();
        new HawcTooltip(opts).show(e, title, content);
    }
}

export default Group;
