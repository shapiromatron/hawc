import _ from 'underscore';


class GroupDescription {

    constructor(data){
        this.data = data;
    }

    build_tr(footnotes){
        var d = this.data,
            mean = '-',
            variance = '-',
            upper = '-',
            lower = '-';

        if (_.isNumber(d.mean))
            mean = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.mean, d.mean_type);
        if (_.isNumber(d.variance))
            variance = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.variance, d.variance_type);
        if (_.isNumber(d.upper))
            upper = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.upper, d.upper_type);
        if (_.isNumber(d.lower))
            lower = '{0}<br><span class="help-inline">{1}</span>'.printf(
                d.lower, d.lower_type);

        return [
            d.description,
            mean,
            variance,
            lower,
            upper,
            d.is_calculated,
        ];
    }

}

export default GroupDescription;
