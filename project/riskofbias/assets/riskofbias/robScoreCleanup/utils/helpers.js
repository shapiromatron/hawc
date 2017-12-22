import shared from 'shared/utils/helpers';

var helpers = Object.assign({}, shared, {
    scores: {
        0: {
            shade: '#E8E8E8',
            text: 'Not applicable',
        },
        1: {
            shade: '#CC3333',
            text: 'Definitely high risk of bias',
        },
        2: {
            shade: '#FFCC00',
            text: 'Probably high risk of bias',
        },
        3: {
            shade: '#6FFF00',
            text: 'Probably low risk of bias',
        },
        4: {
            shade: '#00CC00',
            text: 'Definitely low risk of bias',
        },
        10: {
            shade: '#E8E8E8',
            text: 'Not Reported',
        },
    },
    getScoreInfo(score) {
        return this.scores[score];
    },
    buildPatchUrl(config, ids) {
        return shared.getBulkUrl(
            config.host,
            shared.getUrlWithAssessment(config.items.patchUrl, config.assessment_id),
            ids
        );
    },
});

export default helpers;
