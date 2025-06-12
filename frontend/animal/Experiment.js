import DssTox from "assessment/DssTox";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

class Experiment {
    constructor(data) {
        this.data = data;
        this.dsstox = data.dtxsid !== null ? new DssTox(data.dtxsid) : null;
        delete data.dtxsid;
    }

    static get_detail_url(id) {
        return `/ani/experiment/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/ani/api/experiment/${id}/`, d => cb(new Experiment(d)));
    }

    static displayAsModal(id) {
        Experiment.get_object(id, d => d.displayAsModal());
    }

    static displayFullPager($el, id) {
        Experiment.get_object(id, d => d.displayFullPager($el));
    }

    build_breadcrumbs() {
        var urls = [
            {
                url: this.data.study.url,
                name: this.data.study.short_citation,
            },
            {
                url: this.data.url,
                name: this.data.name,
            },
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    build_details_table() {
        var self = this,
            getGenerations = function () {
                return self.data.is_generational ? "Yes" : "No";
            },
            getPurityText = function () {
                return self.data.purity_available ? "Chemical purity" : "Chemical purity available";
            },
            getPurity = function () {
                var qualifier =
                    self.data.purity_qualifier === "=" ? "" : self.data.purity_qualifier;
                return self.data.purity ? `${qualifier}${self.data.purity}%` : "No";
            },
            tbl;

        tbl = new DescriptiveTable()
            .add_tbody_tr("Name", this.data.name)
            .add_tbody_tr("Type", this.data.type)
            .add_tbody_tr("Multiple generations", getGenerations())
            .add_tbody_tr("Chemical", this.data.chemical)
            .add_tbody_tr("CAS", this.data.cas)
            .add_tbody_tr("DTXSID", this.dsstox ? this.dsstox.verbose_link() : null)
            .add_tbody_tr("Chemical source", this.data.chemical_source)
            .add_tbody_tr(getPurityText(), getPurity())
            .add_tbody_tr("Vehicle", this.data.vehicle)
            .add_tbody_tr("Animal diet", this.data.diet)
            .add_tbody_tr("Guideline compliance", this.data.guideline_compliance)
            .add_tbody_tr("Comments", this.data.description);

        return tbl.get_tbl();
    }

    displayFullPager($div) {
        $div.hide();
        this.render($div);
        $div.fadeIn();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            title = $("<h4>").html(this.build_breadcrumbs()),
            $details = $('<div class="col-md-12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row">').append($details)
            );

        $details.append(this.build_details_table());

        if (this.dsstox) {
            let el = $('<div class="row">');
            this.dsstox.renderChemicalDetails(el[0], true);
            $details.append(el);
        }

        modal.addHeader(title).addBody($content).addFooter("").show({maxWidth: 1000});
    }

    render($div) {
        let dsstox = $("<div>");
        if (this.dsstox) {
            this.dsstox.renderChemicalDetails(dsstox[0], true);
            $div.append(dsstox);
        }
        $div.append(this.build_details_table(), dsstox);
    }
}

export default Experiment;
