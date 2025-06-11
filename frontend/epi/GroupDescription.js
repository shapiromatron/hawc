import _ from "lodash";

class GroupDescription {
    constructor(data) {
        this.data = data;
    }

    build_tr(_footnotes) {
        var d = this.data,
            mean = "-",
            variance = "-",
            upper = "-",
            lower = "-";

        if (_.isNumber(d.mean))
            mean = `${d.mean}<br><span class="text-muted">${d.mean_type}</span>`;
        if (_.isNumber(d.variance))
            variance = `${d.variance}<br><span class="text-muted">${d.variance_type}</span>`;
        if (_.isNumber(d.upper))
            upper = `${d.upper}<br><span class="text-muted">${d.upper_type}</span>`;
        if (_.isNumber(d.lower))
            lower = `${d.lower}<br><span class="text-muted">${d.lower_type}</span>`;

        return [d.description, mean, variance, lower, upper, d.is_calculated];
    }
}

export default GroupDescription;
