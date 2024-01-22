export const getReferenceTagListUrl = function (assessmentId, tagId) {
    return `/lit/assessment/${assessmentId}/references/?tag_id=${tagId}`;
};
