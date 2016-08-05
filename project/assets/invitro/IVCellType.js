import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';

class IVCellType {

    constructor(data){
        this.data = data;
    }

    static get_object(id, cb){
        $.get('/in-vitro/api/celltype/{0}/'.printf(id), function(d){
            cb(new IVCellType(d));
        });
    }

    static displayAsModal(id){
        IVCellType.get_object(id, function(d){d.displayAsModal();});
    }

    static displayAsPage(id, div){
        IVCellType.get_object(id, function(d){d.displayAsPage(div);});
    }

    build_title(){
        var el = $('<h1>').text(this.data.title);
        if (window.canEdit){
            var urls = [
                'Cell type editing',
                {url: this.data.url_update, text: 'Update'},
                {url: this.data.url_delete, text: 'Delete'},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    }

    build_details_table(){
        return new DescriptiveTable()
            .add_tbody_tr('Cell type', this.data.cell_type)
            .add_tbody_tr('Tissue', this.data.tissue)
            .add_tbody_tr('Species', this.data.species)
            .add_tbody_tr('Strain', this.data.strain)
            .add_tbody_tr('Sex', this.data.sex_symbol)
            .add_tbody_tr('Cell source', this.data.source)
            .add_tbody_tr('Culture type', this.data.culture_type)
            .get_tbl();
    }

    displayAsModal(){
        var modal = new HAWCModal(),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        $details.append(this.build_details_table());
        modal
            .addTitleLinkHeader(this.data.title, this.data.url)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 900});
    }

    displayAsPage($div){
        $div
            .append(this.build_title())
            .append(this.build_details_table());
    }

}

export default IVCellType;
