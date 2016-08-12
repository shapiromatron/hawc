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
    caseToWords(string){
        return string
            // replace underscores and dashes with spaces
            .replace(/[_-]/g, ' ')
            // insert a space between lower followed by upper
            .replace(/([a-z])([A-Z])/g, '$1 $2')
            // insert a space between last upper in sequence followed by lower
            .replace(/\b([A-Z]+)([A-Z])([a-z])/, '$1 $2$3')
            // uppercase the first character of first word
            .replace(/\w\S*/, function(txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            });
    },
    extendBreadcrumbs(url){
        $('.breadcrumb').children().last().contents().eq(-2).wrap(`<a href=${url}></a>`);
    },
});

export default helpers;
