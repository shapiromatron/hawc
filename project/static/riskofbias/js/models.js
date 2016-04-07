var RiskOfBiasCollection = function(objs){
    this.object_list = objs;
};
_.extend(RiskOfBiasCollection, {
    get_list: function(id, cb){
        $.get('/study/api/study/?assessment_id={0}'.printf(id), function(ds){
            var objs = _.map(ds, function(d){ return new RiskOfBias(d); });
            cb(new RiskOfBiasCollection(objs));
        });
    },
    render: function(id, $div){
        RiskOfBiasCollection.get_list(id, function(d){d.render($div);});
    },
});
RiskOfBiasCollection.prototype = {
    render: function($el){
        $el.hide()
            .append(this.build_filters())
            .append(this.build_table())
            .fadeIn();

        this.registerEvents($el);
    },
    build_filters: function(){
        var $el = $('<div class="row-fluid">'),
            filters = _.chain(this.object_list)
                       .map(function(d){return d.data.study_type;})
                       .uniq()
                       .value();

        if (filters.length>1){
            $el.html(
                $('<select class="span12" size="6" multiple>').html(_.map(filters, function(d){
                    return '<option value="{0}" selected>{0}</option>'.printf(d);
                }))
            );
        }
        return $el;
    },
    build_table: function(){
        var self = this,
            tbl = new BaseTable(),
            colgroups = [25, 60, 15],
            header = ['Short citation', 'Full citation', 'Study type'];

        tbl.addHeaderRow(header);
        tbl.setColGroup(colgroups);

        _.each(this.object_list, function(d){
            tbl.addRow(d.build_row()).data('obj', d);
        });

        return tbl.getTbl();
    },
    registerEvents: function($el){
        var trs = _.map($el.find('table tbody tr'), $),
            vals;
        $el.find('select').on('change', function(e){
            vals = $(this).val();
            _.each(trs, function(tr){
                tr.toggle(vals.indexOf(tr.data('obj').data.study_type)>=0);
            });
        });
    },
};

var RiskOfBias = function(data){
    this.data = data;
};
RiskOfBias.prototype = {
    get_url: function(){
        return '<a href="/rob{0}">{1}</a>'.printf(this.data.url, this.data.short_citation);
    },
    build_row: function(){
        return [this.get_url(), this.data.full_citation, this.data.study_type];
    },
};
