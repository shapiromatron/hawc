export default {
    assessment: {
        name: 'Assessment Cleanup',
        url: '/assessment/:id/clean-extracted-data/',
    },
    fields: {
        name: 'Cleanup Field Selection',
        url: '/assessment/:id/clean-extracted-data/:type/',
    },
    endpoints: {
        name: 'Endpoint Cleanup',
        url: '/assessment/:id/clean-extracted-data/:type/:field/',
    },
};
