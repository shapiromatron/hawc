import $ from "$";

class IVEndpointGroup {
    constructor(data) {
        this.data = data;
    }

    build_row(tbl, opts) {
        var tr = $("<tr>"),
            getDose = function(dose) {
                var txt = dose;
                if (opts.isNOEL)
                    txt += tbl.footnotes.add_footnote("NOEL (No Observed Effect Level)");
                if (opts.isLOEL)
                    txt += tbl.footnotes.add_footnote("LOEL (Lowest Observed Effect Level)");
                return txt;
            },
            getNumeric = function(val) {
                return $.isNumeric(val) ? val.toHawcString() : "-";
            };

        tr.append("<td>{0}</td>".printf(getDose(this.data.dose)));

        if (opts.hasN) tr.append("<td>{0}</td>".printf(getNumeric(this.data.n)));

        if (opts.hasResponse) tr.append("<td>{0}</td>".printf(getNumeric(this.data.response)));

        if (opts.hasVariance) tr.append("<td>{0}</td>".printf(getNumeric(this.data.variance)));

        if (opts.hasDiffControl) tr.append("<td>{0}</td>".printf(this.data.difference_control));

        if (opts.hasSigControl) tr.append("<td>{0}</td>".printf(this.data.significant_control));

        if (opts.hasCytotox) tr.append("<td>{0}</td>".printf(this.data.cytotoxicity_observed));

        if (opts.hasPrecip) tr.append("<td>{0}</td>".printf(this.data.precipitation_observed));

        return tr;
    }
}

export default IVEndpointGroup;
