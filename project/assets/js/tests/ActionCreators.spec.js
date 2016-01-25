import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as assessmentActions from '../actions/Assessment';
import * as endpointActions from '../actions/Endpoint';
import { loadConfig } from '../actions/Config';
import * as types from '../constants/ActionTypes';
import nock from 'nock';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('config action', () => {
    it('should return a config action object', () => {
        let action = loadConfig();

        expect(action).to.deep.equal({
            type: types.CF_LOAD,
        });
    });
});

describe('async actions', () => {
    afterEach(() => {
        nock.cleanAll();
    });

    describe('Assessment actions', () => {

        it('should create an action to load an assessment', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/assessment/api/endpoints/?assessment_id=57')
                .reply(200, {
                    "name": "test assessment",
                    "id": 57,
                    "items": [
                        {
                            "count": 1,
                        },
                    ],
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                { type: types.AS_RECEIVE_OBJECT, item: {
                    "name": "test assessment",
                    "id": 57,
                    "items": [
                        {
                            "count": 1,
                        },
                    ],
                } },
            ];
            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    assessment: "assessment/api/endpoints/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: {} }, expectedActions, done);
            store.dispatch(assessmentActions.fetchObjectIfNeeded(57));
        });
    });

    describe('Endpoint actions', () => {

        it('should load the endpoint model', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/ani/api/cleanup/fields/?assessment_id=57')
                .reply(200, {
                    "text_cleanup_fields": [
                        "system",
                        "organ",
                        "effect",
                        "effect_subtype",
                    ],
                });

            const expectedActions = [
                { type: types.EP_REQUEST },
                { type: types.EP_RECEIVE_MODEL, model: { text_cleanup_fields: [
                    "system",
                    "organ",
                    "effect",
                    "effect_subtype",
                ]}},
            ];
            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    ani: "ani/api/cleanup/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: {},
                endpoint: { isFetching: false,
                            type: 'ani'}}, expectedActions, done);
            store.dispatch(endpointActions.fetchModelIfNeeded(57));
        });

        it('should delete an object', (done) => {
            nock('http://127.0.0.1:9000')
                .delete('/ani/api/cleanup/?assessment_id=57')
                .reply(204, {});

            const expectedActions = [
                { type: types.EP_DELETE_OBJECT, id: 10210 },
            ];

            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    ani: "ani/api/cleanup/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: {},
                endpoint: {
                    items: [
                        {
                            "id": 10210,
                            "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                            "system": "digestive system",
                        },
                        {
                            "id": 10212,
                            "name": "gross body weight (start of experiment)",
                            "system": "systemic",
                        },
                    ],
                    type: 'ani',
                }}, expectedActions, done);
            store.dispatch(endpointActions.deleteObject(57, 10210));
        });

        it('should patch multiple objects', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/ani/api/cleanup/?assessment_id=57')
                .reply(200, [
                    {
                        "id": 10210,
                        "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                        "system": "digestive system",
                    },
                    {
                        "id": 10212,
                        "name": "gross body weight (start of experiment)",
                        "system": "systemic",
                    },
                ])
                .patch('/ani/api/cleanup/?assessment_id=57&ids=10210,10212')
                .reply(200, {});

            const patchList = [{ ids: [10210, 10212], patch: {'system': "Digestive Systems"}}];
            const expectedActions = [
                { type: types.EP_CREATE_EDIT_OBJECT, object: { ids: [10210, 10212], patch: {"system": "Digestive Systems"}}},
                { type: types.EP_REQUEST },
                { type: types.EP_RECEIVE_OBJECTS, items: [
                    {
                        "id": 10210,
                        "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                        "system": "Digestive Systems",
                    },
                    {
                        "id": 10212,
                        "name": "gross body weight (start of experiment)",
                        "system": "Digestive Systems",
                    },
                ]},
                { type: types.EP_RESET_EDIT_OBJECT },
            ];

            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    ani: "ani/api/cleanup/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: { id: 57 },
                endpoint: {
                    items: [
                        {
                            "id": 10210,
                            "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                            "system": "digestive system",
                        },
                        {
                            "id": 10212,
                            "name": "gross body weight (start of experiment)",
                            "system": "systemic",
                        },
                    ],
                    type: 'ani',
                }}, expectedActions, done);
            store.dispatch(endpointActions.patchObjectList(patchList));
        });

    });
});
