import _ from 'underscore';

import EndpointAggregation from 'summary/EndpointAggregation';

import BaseVisualForm from './BaseVisualForm';


class EndpointAggregationForm extends BaseVisualForm {

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

