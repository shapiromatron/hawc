import shared from 'shared/utils/helpers';

var helpers = Object.assign({}, shared, {
    getObjectUrl(base, id){
        return `${base}${id}/`;
    },
    getTestUrl(host, route){
        return `${host}${route}`;
    },
    getEndpointsUrl(config, study_id=[], effect=[]){
        let effects = effect.join(','),
            study_ids = study_id.join(',');
        return `${config.host}${config.endpoint_filter_url}&study_id[]=${study_ids}&effect[]=${effects}`;
    },
    errorDict: {
        endpoints: 'Filtering results contain more than 100 endpoints. Increase the quality threshold or include fewer effects.',
        effects: 'At least one effect must be chosen.',
        empty: 'No endpoints were returned. Decrease the quality threshold or include more effects.',
    },
    formatErrors(error){
        error  = error.substr(-9);
        return helpers.errorDict[error];
    },
});

export default helpers;
