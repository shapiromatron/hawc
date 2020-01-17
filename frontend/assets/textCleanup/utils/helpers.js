import shared from "shared/utils/helpers";

var helpers = Object.assign({}, shared, {
    getAssessmentApiUrl(config) {
        return `${config.host}${config.assessment}?assessment_id=${config.assessment_id}`;
    },
    getItemApiURL({
        state,
        filterFields = false,
        fetchModel = false,
        ids = null,
        routerParams = {},
    }) {
        let getFields = fetchModel ? "fields/" : "",
            {field, id, type} = routerParams,
            fields = filterFields && field ? `&fields=${field}` : "",
            idList = ids ? `&ids=${ids}` : "";
        return `${state.config.host}${state.config[type].url}${getFields}?assessment_id=${id}${fields}${idList}`;
    },
    getObjectUrl(base, id) {
        return `${base}${id}/`;
    },
    extendBreadcrumbs(url) {
        $(".breadcrumb")
            .children()
            .last()
            .contents()
            .eq(-2)
            .wrap(`<a href=${url}></a>`);
    },
});

export default helpers;
