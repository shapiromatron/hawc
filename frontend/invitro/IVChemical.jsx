import DssTox from "assessment/DssTox";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

class IVChemical {
    constructor(data) {
        this.data = data;
        this.dsstox = data.dtxsid !== null ? new DssTox(data.dtxsid) : null;
        delete data.dtxsid;
    }

    static get_detail_url(id) {
        return `/in-vitro/chemical/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/in-vitro/api/chemical/${id}/`, d => cb(new IVChemical(d)));
    }

    static displayAsModal(id) {
        IVChemical.get_object(id, d => d.displayAsModal());
    }

    static displayAsPage(id, div) {
        IVChemical.get_object(id, d => d.displayAsPage(div));
    }

    build_title() {
        var el = $("<div class='d-flex'>").append($("<h2>").text(this.data.name));
        if (window.canEdit) {
            var urls = [
                "Chemical editing",
                {href: this.data.url_update, text: "Update"},
                {href: this.data.url_delete, text: "Delete"},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    }

    build_details_table() {
        return new DescriptiveTable()
            .add_tbody_tr("Chemical name", this.data.name)
            .add_tbody_tr("CAS", this.data.cas)
            .add_tbody_tr("DTXSID", this.dsstox ? this.dsstox.verbose_link() : null)
            .add_tbody_tr("CAS inferred?", HAWCUtils.booleanCheckbox(this.data.cas_inferred))
            .add_tbody_tr("CAS notes", this.data.cas_notes)
            .add_tbody_tr("Source", this.data.source)
            .add_tbody_tr("Purity", this.data.purity)
            .add_tbody_tr(
                "Purity confirmed?",
                HAWCUtils.booleanCheckbox(this.data.purity_confirmed)
            )
            .add_tbody_tr("Purity notes", this.data.purity_confirmed_notes)
            .add_tbody_tr("Dilution/storage/precipitation notes", this.data.dilution_storage_notes)
            .get_tbl();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
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

        modal
            .addTitleLinkHeader(this.data.name, this.data.url)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }

    displayAsPage($div) {
        $div.append(this.build_title()).append(this.build_details_table());
        if (this.dsstox) {
            let el = $("<div>");
            this.dsstox.renderChemicalDetails(el[0], true);
            $div.append(el);
        }
    }
}

export default IVChemical;
