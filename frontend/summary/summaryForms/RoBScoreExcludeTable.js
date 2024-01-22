import _ from "lodash";

import $ from "$";

import {TableField} from "./TableFields";

class RoBScoreExcludeTable extends TableField {
    constructor(...props) {
        super(...props);
    }
    renderHeader() {
        return $("<tr>")
            .append("<th>Display</th><th>Metric</th><th>Study</th><th>Judgment</th>")
            .appendTo(this.$thead);
    }

    addRow() {
        return $("<tr>")
            .append(
                this.addTdCheckbox("included", true),
                this.addTdP("metric", ""),
                this.addTdP("study", ""),
                this.addTdP("score", "")
            )
            .appendTo(this.$tbody);
    }

    fromSerialized() {
        let scores = new Set(this.parent.settings.excluded_score_ids),
            rows = [];
        this.parent.data.studies.forEach(study => {
            study.riskofbiases
                .filter(d => d.final === true && d.active === true)
                .forEach(robs => {
                    robs.scores.forEach(score => {
                        const metric = score.metric.use_short_name
                                ? score.metric.short_name
                                : score.metric.name,
                            label = score.label ? score.label : "&lt;none&gt;",
                            scoreType = score.is_default ? " (overall)" : " (override)";

                        rows.push({
                            id: score.id,
                            included: !scores.has(score.id),
                            study: score.study_name,
                            metric,
                            score: `<span><b>Label:</b>&nbsp;${label} ${scoreType}</span><br/>
                            <span><b>Judgment:</b>&nbsp;${score.score_description}&nbsp;(${score.score_symbol})</span>`,
                        });
                    });
                });
        });

        this.$tbody.empty();
        _.each(rows, d => {
            var row = this.addRow();
            row.find(".score").html(d.score);
            row.find(".study").text(d.study);
            row.find(".metric").text(d.metric);
            row.find('input[name="included"]').prop("checked", d.included).data("id", d.id);
        });
    }

    toSerializedRow(row) {
        var inp = $(row).find('input[name="included"]');
        return inp.prop("checked") === false ? inp.data("id") : null;
    }
}

export default RoBScoreExcludeTable;
