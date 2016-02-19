export default {
    assessment: {
        name: 'Assessment cleanup',
        url: '/assessment/:id/clean-extracted-data/',
    },
    fields: {
        name: 'Cleanup field selection',
        url: '/assessment/:id/clean-extracted-data/:type/',
    },
    endpoints: {
        name: 'Endpoint cleanup',
        url: '/assessment/:id/clean-extracted-data/:type/:field/',
    },
};
