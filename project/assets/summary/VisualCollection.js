class VisualCollection {

    constructor(data){
        this.visuals = [];
        for(var i=0; i<data.length; i++){
            this.visuals.push(new Visual(data[i]));
        }
    }

    static buildTable(url1, url2, $el){
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
            obj = new VisualCollection( visuals );
            return obj.build_table($el);
        });
    }

    build_table($el){
        if(this.visuals.length === 0)
            return $el.html('<p><i>No custom-visuals are available for this assessment.</i></p>');

        var tbl = new BaseTable();
        tbl.addHeaderRow(['Title', 'Visual type', 'Description', 'Created', 'Modified']);
        tbl.setColGroup([20, 20, 38, 11, 11]);
        for(var i=0; i<this.visuals.length; i++){
            tbl.addRow(this.visuals[i].build_row());
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
                .unshift(this.null_filter)
                .map(function(d){
                    return '<option value="{0}">{1}</option>'.printf(d, d);
                }).value();

        return $('<div>').append(
            '<label class="control-label">Filter by visualization type:</label>',
            $('<select>').append(types).change(this.filterRows.bind(this))
        );
    }

    filterRows(e){
        var filter = (e)? e.target.value: this.null_filter,
            isNullFilter = (filter === this.null_filter);

        this.$tbl.find('tbody tr').each(function(){
            if (isNullFilter || this.innerHTML.indexOf(filter)>=0){
                this.style.display = null;
            } else {
                this.style.display = 'none';
            }
        });
    }

}

VisualCollection.null_filter = '---';

export default VisualCollection;
