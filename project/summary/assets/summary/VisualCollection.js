import $ from '$';
import _ from 'underscore';

import Tablesort from 'tablesort';

import BaseTable from 'utils/BaseTable';
import HAWCUtils from 'utils/HAWCUtils';

import BaseVisual from './BaseVisual';


const NULL_FILTER = '---';

class VisualCollection {

    constructor(data, opts){
        this.visuals = [];
        this.opts = opts;
        for(var i=0; i<data.length; i++){
            this.visuals.push(new BaseVisual(data[i]));
        }
    }

    static buildTable(url1, url2, $el, opts){
        var visuals, obj;

        $.when(
           $.get(url1),
           $.get(url2)
        ).done(function(d1, d2) {
            d1[0].push.apply(d1[0], d2[0]);
            visuals = _.sortBy(d1[0], function(d){return d.title;});
        }).fail(function(){
            HAWCUtils.addAlert('Error- unable to fetch visualizations; please contact a HAWC administrator.');
            visuals = [];
        }).always(function(){
            obj = new VisualCollection(visuals, opts);
            return obj.build_table($el);
        });
    }

    build_table($el){
        if(this.visuals.length === 0)
            return $el.html('<p><i>No custom-visuals are available for this assessment.</i></p>');

        let tbl = new BaseTable(),
            headers = ['Title', 'Visual type', 'Description', 'Created', 'Modified'],
            headerWidths = [20, 20, 36, 12, 12];

        if (this.opts.showPublished){
            headers.splice(3, 0, 'Published');
            headerWidths = [20, 20, 30, 8, 11, 11];
        }

        tbl.addHeaderRow(headers);
        tbl.setColGroup(headerWidths);
        for(var i=0; i<this.visuals.length; i++){
            tbl.addRow(this.visuals[i].build_row(this.opts));
        }
        $el
            .append(this.setTableFilter())
            .append(tbl.getTbl());
        this.$tbl = $($el.find('table'));
        this.setTableSorting(this.$tbl);
        return $el;
    }

    setTableSorting(){
        var name = this.$tbl.find('thead tr th')[0];
        name.setAttribute('class', (name.getAttribute('class') || '') + ' sort-default');
        new Tablesort(this.$tbl[0]);
    }

    setTableFilter(){
        var types = _.chain(this.visuals)
                .pluck('data')
                .pluck('visual_type')
                .sort()
                .uniq(true)
                .unshift(NULL_FILTER)
                .map((d) =>`<option value="${d}">${d}</option>`)
                .value();

        return $('<div>').append(
            '<label class="control-label">Filter by visualization type:</label>',
            $('<select>').append(types).change(this.filterRows.bind(this))
        );
    }

    filterRows(e){
        var filter = (e)? e.target.value: NULL_FILTER,
            isNullFilter = (filter === NULL_FILTER);

        this.$tbl.find('tbody tr').each(function(){
            if (isNullFilter || this.innerHTML.indexOf(filter)>=0){
                this.style.display = null;
            } else {
                this.style.display = 'none';
            }
        });
    }

}

export default VisualCollection;
