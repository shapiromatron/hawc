import $ from "$";
import h from "shared/utils/helpers";

class IVEndpointGroup {
    constructor(data) {
        this.data = data;
    }

    build_row(tbl, opts) {
        var tr = $("<tr>"),
            getDose = function (dose) {
                var txt = dose;
                if (opts.isNOEL)
                    txt += tbl.footnotes.add_footnote("NOEL (No Observed Effect Level)");
                if (opts.isLOEL)
                    txt += tbl.footnotes.add_footnote("LOEL (Lowest Observed Effect Level)");
                return txt;
            },
            getNumeric = function (val) {
                return $.isNumeric(val) ? h.ff(val) : "-";
            };

        tr.append(`<td>${getDose(this.data.dose)}</td>`);

        if (opts.hasN) {
            tr.append(`<td>${getNumeric(this.data.n)}</td>`);
        }

        if (opts.hasResponse) {
            tr.append(`<td>${getNumeric(this.data.response)}</td>`);
        }

        if (opts.hasVariance) {
            tr.append(`<td>${getNumeric(this.data.variance)}</td>`);
        }

        if (opts.hasDiffControl) {
            tr.append(`<td>${this.data.difference_control}</td>`);
        }

        if (opts.hasSigControl) {
            tr.append(`<td>${this.data.significant_control}</td>`);
        }

        if (opts.hasCytotox) {
            tr.append(`<td>${this.data.cytotoxicity_observed}</td>`);
        }

        if (opts.hasPrecip) {
            tr.append(`<td>${this.data.precipitation_observed}</td>`);
        }

        return tr;
    }
}

export default IVEndpointGroup;
