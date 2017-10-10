import $ from '$';
import _ from 'underscore';

import BaseTable from 'utils/BaseTable';

import Study from './Study';


class StudyCollection {

    constructor(objs){
        this.object_list = objs;
    }

    static get_list(id, cb){
        $.get('/study/api/study/?assessment_id={0}'.printf(id), function(ds){
            var objs = _.map(ds, function(d){ return new Study(d); });
            cb(new StudyCollection(objs));
        });
    }

    static render(id, $div){
        StudyCollection.get_list(id, function(d){d.render($div);});
    }

    render($el){
        $el.hide()
            .append(this.build_filters())
            .append(this.build_table())
            .fadeIn();

        this.registerEvents($el);
    }

    build_filters(){
        var $el = $('<div class="row-fluid">'),
            flds = [];

        if (this.object_list.filter(function(d){return d.data.bioassay;}).length>0){
            flds.push('bioassay');
        }
        if (this.object_list.filter(function(d){return d.data.epi;}).length>0){
            flds.push('epi');
        }
        if (this.object_list.filter(function(d){return d.data.epi_meta;}).length>0){
            flds.push('epi_meta');
        }
        if (this.object_list.filter(function(d){return d.data.in_vitro;}).length>0){
            flds.push('in_vitro');
        }

        if (flds.length > 1){
            $('<select class="span12" size="6" multiple>')
                .append(_.map(flds, function(d){
                    return '<option value="{0}">{1}</option>'.printf(d, Study.typeNames[d]);
                }))
                .appendTo($el);
        }
        return $el;
    }

    build_table(){
        var tbl = new BaseTable(),
            colgroups = [25, 50, 7, 7, 8, 7],
            header = [
                'Short citation',
                'Full citation',
                'Bioassay',
                'Epidemiology',
                'Epidemiology meta-analysis',
                'In vitro',
            ];

        tbl.addHeaderRow(header);
        tbl.setColGroup(colgroups);

        _.each(this.object_list, function(d){
            tbl.addRow(d.build_row()).data('obj', d);
        });

        return tbl.getTbl();
    }

    registerEvents($el){
        var trs = _.map($el.find('table tbody tr'), $),
            vals;
        $el.find('select').on('change', function(e){
            vals = $(this).val() || $.map($el.find('option'), function(d){return d.value;});

            _.each(trs, function(tr){
                let data = tr.data('obj').data,
                    dataTypes = vals.filter(function(d){return data[d];}).length;
                tr.toggle(dataTypes>0);
            });
        });
    }

}

export default StudyCollection;
