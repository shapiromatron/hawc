export default {
    assessment: {
        name: 'Assessment Cleanup',
        url: '/assessment/:id/endpoint_cleanup/',
    },
    fields: {
        name: 'Cleanup Field Selection',
        url: '/assessment/:id/endpoint_cleanup/:type/',
    },
    endpoints: {
        name: 'Endpoint Cleanup',
        url: '/assessment/:id/endpoint_cleanup/:type/:field/',
    },
};
