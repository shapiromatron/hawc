import $ from '$';

import DescriptiveTable from 'utils/DescriptiveTable';
import HAWCModal from 'utils/HAWCModal';
import HAWCUtils from 'utils/HAWCUtils';
import Study from 'study/Study';
import { fetchFullStudyIfNeeded } from 'robTable/actions';

class Experiment {
    constructor(data){
        this.data = data;
    }

    static get_object(id, cb){
        $.get('/ani/api/experiment/{0}/'.printf(id), function(d){
            cb(new Experiment(d));
        });
    }

    static displayAsModal(id){
        Experiment.get_object(id, function(d){d.displayAsModal();});
    }

    build_breadcrumbs(){
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

    build_pdf_link() {

        this.props.dispatch(fetchFullStudyIfNeeded());
        heroID = this.props.heroid

        return (
            <div>
                <p><a className='btn btn-mini btn-primary' target='_blank' href={'https://hero.epa.gov/hero/index.cfm/reference/downloads/reference_id/' + heroID}>Full text link <i className='fa fa-fw fa-file-pdf-o'></i></a><span>&nbsp;</span></p>
            </div>
        );
    }

    build_details_table(){
        var self = this,
            getGenerations = function(){
                return (self.data.is_generational) ? 'Yes' : 'No';
            },
            getLitterEffects = function(){
                if(self.data.is_generational) return self.data.litter_effects;
            },
            getPurityText = function(){
                return (self.data.purity_available) ? 'Chemical purity' : 'Chemical purity available';
            },
            getPurity = function(){
                var qualifier = (self.data.purity_qualifier === '=') ? '' : self.data.purity_qualifier;
                return (self.data.purity) ? '{0}{1}%'.printf(qualifier, self.data.purity) : 'No';
            },
            tbl, casTd;

        tbl = new DescriptiveTable()
            .add_tbody_tr('Name', this.data.name)
            .add_tbody_tr('Type', this.data.type)
            .add_tbody_tr('Multiple generations', getGenerations())
            .add_tbody_tr('Chemical', this.data.chemical)
            .add_tbody_tr('CAS', this.data.cas)
            .add_tbody_tr('Chemical source', this.data.chemical_source)
            .add_tbody_tr(getPurityText(), getPurity())
            .add_tbody_tr('Vehicle', this.data.vehicle)
            .add_tbody_tr('Animal diet', this.data.diet)
            .add_tbody_tr('Litter effects', getLitterEffects(), {annotate: this.data.litter_effect_notes})
            .add_tbody_tr('Guideline compliance', this.data.guideline_compliance)
            .add_tbody_tr('Description and animal husbandry', this.data.description);

        if (this.data.cas_url){
            casTd = tbl.get_tbl().find('th:contains("CAS")').next();
            HAWCUtils.renderChemicalProperties(this.data.cas_url, casTd, false);
        }

        return tbl.get_tbl();
    }

    displayAsModal(){
        var modal = new HAWCModal(),
            title = $('<h4>').html(this.build_breadcrumbs()),
            $details = $('<div class="span12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row-fluid">').append($details));

        this.render($details);

        modal.addHeader(title)
            .addBody($content)
            .addFooter('')
            .show({maxWidth: 1000});
    }

    render($div){
        $div.append(this.build_details_table());
    }
}

export default Experiment;
