import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import nock from 'nock';

import * as endpointActions from 'textCleanup/actions/Endpoint';
import * as types from 'textCleanup/constants/ActionTypes';

import { HOST } from 'tests/constants';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('textCleanup Endpoint actions', () => {
    describe('async actions', () => {
        afterEach(() => {
            nock.cleanAll();
        });

        it('should load the endpoint model', done => {
            nock(HOST)
                .get('/ani/api/cleanup/fields/?assessment_id=57')
                .reply(200, {
                    text_cleanup_fields: [
                        'system',
                        'organ',
                        'effect',
                        'effect_subtype',
                    ],
                });

            const expectedActions = [
                { type: types.EP_REQUEST },
                {
                    type: types.EP_RECEIVE_MODEL,
                    model: {
                        text_cleanup_fields: [
                            'system',
                            'organ',
                            'effect',
                            'effect_subtype',
                        ],
                    },
                },
            ];
            const store = mockStore(
                {
                    router: {
                        params: { field: 'system', type: 'ani', id: '57' },
                    },
                    config: {
                        host: HOST,
                        ani: { url: 'ani/api/cleanup/' },
                    },
                    assessment: { active: { id: 57 } },
                    endpoint: {
                        isFetching: false,
                        type: 'ani',
                    },
                },
                expectedActions,
                done
            );
            store.dispatch(endpointActions.fetchModelIfNeeded());
        });

        it('should load endpoint items', done => {
            nock(HOST)
                .get('/ani/api/cleanup/?assessment_id=57')
                .reply(200, [
                    {
                        id: 10210,
                        name:
                            'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        system: 'digestive system',
                    },
                    {
                        id: 10212,
                        name: 'gross body weight (start of experiment)',
                        system: 'systemic',
                    },
                ]);

            const expectedActions = [
                { type: types.EP_REQUEST },
                {
                    type: types.EP_RECEIVE_OBJECTS,
                    items: [
                        {
                            id: 10210,
                            name:
                                'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                            system: 'digestive system',
                        },
                        {
                            id: 10212,
                            name: 'gross body weight (start of experiment)',
                            system: 'systemic',
                        },
                    ],
                },
            ];

            const store = mockStore(
                {
                    router: { params: { type: 'ani', id: '57' } },
                    config: {
                        host: HOST,
                        ani: { url: 'ani/api/cleanup/' },
                    },
                    assessment: { active: { id: 57 } },
                    endpoint: {
                        isFetching: false,
                        field: 'system',
                        type: 'ani',
                    },
                },
                expectedActions,
                done
            );
            store.dispatch(endpointActions.fetchObjectsIfNeeded());
        });

        it('should bulk patch multiple objects', done => {
            nock(HOST)
                .patch('/ani/api/cleanup/?assessment_id=57&ids=10210,10212')
                .reply(200, {})
                .get('/ani/api/cleanup/?assessment_id=57')
                .reply(200, [
                    {
                        id: 10210,
                        name:
                            'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        system: 'Digestive Systems',
                    },
                    {
                        id: 10212,
                        name: 'gross body weight (start of experiment)',
                        system: 'Digestive Systems',
                    },
                ]);

            const patchList = {
                ids: [10210, 10212],
                field: 'system',
                system: 'Digestive Systems',
                stale: 'digestive system',
            };
            const expectedActions = [
                { type: types.EP_RESET_EDIT_OBJECT, field: 'digestive system' },
                {
                    type: types.EP_CREATE_EDIT_OBJECT,
                    object: {
                        ids: [10210, 10212],
                        field: 'system',
                        system: 'Digestive Systems',
                    },
                },
                {
                    type: types.EP_PATCH_OBJECTS,
                    patch: {
                        field: 'system',
                        ids: [10210, 10212],
                        system: 'Digestive Systems',
                    },
                },
            ];

            const store = mockStore(
                {
                    router: {
                        params: { field: 'system', type: 'ani', id: '57' },
                    },
                    config: {
                        host: HOST,
                        ani: { url: 'ani/api/cleanup/' },
                    },
                    assessment: { active: { id: 57 } },
                    endpoint: {
                        items: [
                            {
                                id: 10210,
                                name:
                                    'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                                system: 'digestive system',
                            },
                            {
                                id: 10212,
                                name: 'gross body weight (start of experiment)',
                                system: 'digestive system',
                            },
                        ],
                        type: 'ani',
                        field: 'system',
                    },
                },
                expectedActions,
                done
            );
            store.dispatch(endpointActions.patchBulkList(patchList));
        });

        it('should detail patch multiple objects', done => {
            nock(HOST)
                .patch('/ani/api/cleanup/?assessment_id=57&ids=10210,10212')
                .reply(204, {})
                .get('/ani/api/cleanup/?assessment_id=57&ids=10210,10212')
                .reply(200, [
                    {
                        id: 10210,
                        name:
                            'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        system: 'Digestive Systems',
                    },
                    {
                        id: 10212,
                        name: 'gross body weight (start of experiment)',
                        system: 'Digestive Systems',
                    },
                ]);

            const patchList = {
                ids: [10210, 10212],
                field: 'system',
                system: 'Digestive Systems',
                stale: 'digestive system',
            };
            const expectedActions = [
                {
                    type: types.EP_REMOVE_EDIT_OBJECT_IDS,
                    field: 'digestive system',
                    ids: [10210, 10212],
                },
                {
                    type: types.EP_CREATE_EDIT_OBJECT,
                    object: {
                        ids: [10210, 10212],
                        field: 'system',
                        system: 'Digestive Systems',
                    },
                },
                { type: types.EP_REQUEST },
                {
                    type: types.EP_RECEIVE_OBJECT,
                    item: {
                        id: 10210,
                        name:
                            'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        system: 'Digestive Systems',
                    },
                },
                {
                    type: types.EP_RECEIVE_OBJECT,
                    item: {
                        id: 10212,
                        name: 'gross body weight (start of experiment)',
                        system: 'Digestive Systems',
                    },
                },
            ];
            const store = mockStore(
                {
                    router: {
                        params: { field: 'system', type: 'ani', id: '57' },
                    },
                    config: {
                        host: HOST,
                        ani: { url: 'ani/api/cleanup/' },
                    },
                    assessment: { active: { id: 57 } },
                    endpoint: {
                        items: [
                            {
                                id: 10210,
                                name:
                                    'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                                system: 'digestive system',
                            },
                            {
                                id: 10212,
                                name: 'gross body weight (start of experiment)',
                                system: 'digestive system',
                            },
                        ],
                        type: 'ani',
                        field: 'system',
                    },
                },
                expectedActions,
                done
            );
            store.dispatch(endpointActions.patchDetailList(patchList));
        });
    });
});
