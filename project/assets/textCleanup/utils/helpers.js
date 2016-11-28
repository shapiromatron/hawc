import shared from 'shared/utils/helpers';

var helpers = Object.assign({}, shared, {
    getAssessmentApiUrl(config){
        return `${config.host}${config.assessment}?assessment_id=${config.assessment_id}`;
    },
    getItemApiURL(state, filterFields=false, fetchModel=false, ids=null){
        let getFields = fetchModel ? 'fields/' : '',
            fields = (filterFields && state.router.params.field) ? `&fields=${state.router.params.field}` : '',
            idList = ids ? `&ids=${ids}` : '';
        return `${state.config.host}${state.config[state.router.params.type].url}${getFields}?assessment_id=${state.router.params.id}${fields}${idList}`;
    },
    getObjectUrl(base, id){
        return `${base}${id}/`;
    },
    extendBreadcrumbs(url){
        $('.breadcrumb').children().last().contents().eq(-2).wrap(`<a href=${url}></a>`);
    },
});

export default helpers;
