import shared from 'shared/utils/helpers';

var helpers = Object.assign({}, shared, {
    buildPatchUrl(config, ids) {
        return shared.getBulkUrl(
            config.host,
            shared.getUrlWithAssessment(config.items.patchUrl, config.assessment_id),
            ids
        );
    },
});

export default helpers;
