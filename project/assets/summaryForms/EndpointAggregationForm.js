import _ from 'underscore';

import EndpointAggregation from './summary/EndpointAggregation';

import VisualForm from './VisualForm';


class EndpointAggregationForm extends VisualForm {

    constructor($el){
        VisualForm.apply(this, arguments);
    }

    buildPreview($parent, data){
        this.preview = new EndpointAggregation(data).displayAsPage( $parent.empty() );
    }

    updateSettingsFromPreview(){
    }
}

_.extend(EndpointAggregationForm, {
    schema: [],
});

export default EndpointAggregationForm;

