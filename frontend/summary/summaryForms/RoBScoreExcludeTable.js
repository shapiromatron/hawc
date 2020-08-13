import _ from "lodash";
import $ from "$";

import {TableField} from "./TableFields";

class RoBScoreExcludeTable extends TableField {
    constructor(...props) {
        super(...props);
    }
    renderHeader() {
        return $("<tr>")
            .append("<th>Display</th>", "<th>Score</th>")
            .appendTo(this.$thead);
    }

    addRow() {
        var includeTd = this.addTdCheckbox("included", true),
            scoreTd = this.addTdP("description", "");

        return $("<tr>")
            .append(includeTd, scoreTd)
            .appendTo(this.$tbody);
    }

    fromSerialized() {
        window._ = _;
        window.el = this;
        let scores = new Set(this.parent.settings.excluded_score_ids),
            rows = [];
        this.parent.data.studies.forEach(study => {
            study.riskofbiases
                .filter(d => d.final === true && d.active === true)
                .forEach(robs => {
                    robs.scores.forEach(score => {
                        rows.push({
                            id: score.id,
                            included: !scores.has(score.id),
                            description: `<ul>
                            <li><b>Study:</b>&nbsp;${score.study_name}</li>
                            <li><b>Metric:</b>&nbsp;${score.metric.name}</li>
                            <li><b>Label:</b>&nbsp;${score.label} (${
                                score.is_default ? "overall" : "override"
                            })</li>
                            <li><b>Score:</b>&nbsp;${score.score_description}</li>
                        </ul>`,
                        });
                    });
                });
        });

        this.$tbody.empty();
        _.each(rows, d => {
            var row = this.addRow();
            row.find(".description").html(d.description);
            row.find('input[name="included"]')
                .prop("checked", d.included)
                .data("id", d.id);
        });
    }

    toSerializedRow(row) {
        var inp = $(row).find('input[name="included"]');
        return inp.prop("checked") === false ? inp.data("id") : null;
    }
}

export default RoBScoreExcludeTable;
