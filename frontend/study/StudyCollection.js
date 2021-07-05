import $ from "$";
import _ from "lodash";

import BaseTable from "shared/utils/BaseTable";

import Study from "./Study";

class StudyCollection {
    constructor(objs) {
        this.object_list = objs;
    }

    static get_list(id, cb) {
        $.get(`/study/api/study/?assessment_id=${id}`, function(ds) {
            var objs = _.map(ds, d => new Study(d));
            cb(new StudyCollection(objs));
        });
    }

    static render(id, $div) {
        StudyCollection.get_list(id, d => d.render($div));
    }

    render($el) {
        const noun = this.object_list.length === 1 ? "study" : "studies";
        $el.hide()
            .append(this.build_filters())
            .append(this.build_table())
            .append(`<p><b>${this.object_list.length} ${noun} available.</b></p>`)
            .fadeIn();

        this.registerEvents($el);
    }

    build_filters() {
        var flds = [];

        if (this.object_list.filter(d => d.data.bioassay).length > 0) {
            flds.push("bioassay");
        }
        if (this.object_list.filter(d => d.data.epi).length > 0) {
            flds.push("epi");
        }
        if (this.object_list.filter(d => d.data.epi_meta).length > 0) {
            flds.push("epi_meta");
        }
        if (this.object_list.filter(d => d.data.in_vitro).length > 0) {
            flds.push("in_vitro");
        }

        if (flds.length > 1) {
            return $('<select class="form-control" size="4" multiple>').append(
                _.map(flds, d => `<option value="${d}">${Study.typeNames[d]}</option>`)
            );
        }
    }

    build_table() {
        if (this.object_list.length === 0) {
            return;
        }
        var tbl = new BaseTable(),
            colgroups = [25, 50, 7, 7, 8, 7],
            header = [
                "Short citation",
                "Full citation",
                "Bioassay",
                "Epidemiology",
                "Epidemiology meta-analysis",
                "In vitro",
            ];

        tbl.addHeaderRow(header);
        tbl.setColGroup(colgroups);

        _.each(this.object_list, function(d) {
            tbl.addRow(d.build_row()).data("obj", d);
        });

        return tbl.getTbl();
    }

    registerEvents($el) {
        var trs = _.map($el.find("table tbody tr"), $),
            vals;
        $el.find("select").on("change", function(e) {
            vals =
                $(this).val() ||
                $.map($el.find("option"), function(d) {
                    return d.value;
                });

            _.each(trs, function(tr) {
                let data = tr.data("obj").data,
                    dataTypes = vals.filter(function(d) {
                        return data[d];
                    }).length;
                tr.toggle(dataTypes > 0);
            });
        });
    }
}

export default StudyCollection;
