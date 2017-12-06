import $ from '$';

import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';

class IVChemical {
    constructor(data) {
        this.data = data;
    }

    static get_object(id, cb) {
        $.get('/in-vitro/api/chemical/{0}/'.printf(id), function(d) {
            cb(new IVChemical(d));
        });
    }

    static displayAsModal(id) {
        IVChemical.get_object(id, function(d) {
            d.displayAsModal();
        });
    }

    static displayAsPage(id, div) {
        IVChemical.get_object(id, function(d) {
            d.displayAsPage(div);
        });
    }

    build_title() {
        var el = $('<h1>').text(this.data.name);
        if (window.canEdit) {
            var urls = [
                'Chemical editing',
                { url: this.data.url_update, text: 'Update' },
                { url: this.data.url_delete, text: 'Delete' },
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    }

    build_details_table() {
        return new DescriptiveTable()
            .add_tbody_tr('Chemical name', this.data.name)
            .add_tbody_tr('CAS', this.data.cas)
            .add_tbody_tr(
                'CAS inferred?',
                HAWCUtils.booleanCheckbox(this.data.cas_inferred)
            )
            .add_tbody_tr('CAS notes', this.data.cas_notes)
            .add_tbody_tr('Source', this.data.source)
            .add_tbody_tr('Purity', this.data.purity)
            .add_tbody_tr(
                'Purity confirmed?',
                HAWCUtils.booleanCheckbox(this.data.purity_confirmed)
            )
            .add_tbody_tr('Purity notes', this.data.purity_confirmed_notes)
            .add_tbody_tr(
                'Dilution/storage/precipitation notes',
                this.data.dilution_storage_notes
            )
            .get_tbl();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row-fluid">').append($details)
            );

        $details.append(this.build_details_table());
        modal
            .addTitleLinkHeader(this.data.name, this.data.url)
            .addBody($content)
            .addFooter('')
            .show({ maxWidth: 900 });
    }

    displayAsPage($div) {
        $div.append(this.build_title()).append(this.build_details_table());
    }
}

export default IVChemical;
