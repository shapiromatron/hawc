import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as endpointActions from '../../actions/Endpoint';
import * as types from '../../constants/ActionTypes';
import nock from 'nock';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('Endpoint actions', () => {

    describe('actions', () =>{

        it('should set the endpoint type', () => {
            let action = endpointActions.setField;

            expect(action('system')).to.deep.equal({
                type: types.EP_SET_FIELD,
                field: 'system',
            });
        });

    });

    describe('async actions', () => {
        afterEach(() => {
            nock.cleanAll();
        });

        it('should load the endpoint model', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/ani/api/cleanup/fields/?assessment_id=57')
                .reply(200,  {
                    'text_cleanup_fields': [
                        'system',
                        'organ',
                        'effect',
                        'effect_subtype',
                    ],
                });

            const expectedActions = [
                { type: types.EP_REQUEST },
                { type: types.EP_RECEIVE_MODEL, model: { text_cleanup_fields: [
                    'system',
                    'organ',
                    'effect',
                    'effect_subtype',
                ]}},
            ];
            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    ani: 'ani/api/cleanup/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: { active: { id: 57 } },
                endpoint: { isFetching: false,
                            type: 'ani'}}, expectedActions, done);
            store.dispatch(endpointActions.fetchModelIfNeeded());
        });

        it('should load endpoint items', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/ani/api/cleanup/?assessment_id=57&fields=system')
                .reply(200, [
                    {
                        'id': 10210,
                        'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        'system': 'digestive system',
                    },
                    {
                        'id': 10212,
                        'name': 'gross body weight (start of experiment)',
                        'system': 'systemic',
                    },
                ]);

            const expectedActions = [
                { type: types.EP_REQUEST },
                { type: types.EP_RECEIVE_OBJECTS,
                  items: [
                      {
                          'id': 10210,
                          'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                          'system': 'digestive system',
                      },
                      {
                          'id': 10212,
                          'name': 'gross body weight (start of experiment)',
                          'system': 'systemic',
                      },
                  ],
                },
            ];

            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    ani: 'ani/api/cleanup/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: { active: { id: 57 } },
                endpoint: {
                    isFetching: false,
                    field: 'system',
                    type: 'ani',
                },
            }, expectedActions, done);
            store.dispatch(endpointActions.fetchObjectsIfNeeded(57));
        });

        it('should delete an object', (done) => {
            nock('http://127.0.0.1:9000')
                .delete('/ani/api/cleanup/?assessment_id=57')
                .reply(204, {});

            const expectedActions = [
                { type: types.EP_DELETE_OBJECT, id: 10210 },
            ];

            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    ani: 'ani/api/cleanup/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: { active: { id: 57 } },
                endpoint: {
                    items: [
                        {
                            'id': 10210,
                            'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                            'system': 'digestive system',
                        },
                        {
                            'id': 10212,
                            'name': 'gross body weight (start of experiment)',
                            'system': 'systemic',
                        },
                    ],
                    type: 'ani',
                    field: 'system',
                }}, expectedActions, done);
            store.dispatch(endpointActions.deleteObject(10210));
        });

        it('should patch multiple objects', (done) => {
            nock('http://127.0.0.1:9000')
                .patch('/ani/api/cleanup/?assessment_id=57&ids=10210')
                .reply(200, {})
                .patch('/ani/api/cleanup/?assessment_id=57&ids=10212')
                .reply(200, {})
                .get('/ani/api/cleanup/?assessment_id=57')
                .reply(200, [
                    {
                        'id': 10210,
                        'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                        'system': 'Digestive Systems',
                    },
                    {
                        'id': 10212,
                        'name': 'gross body weight (start of experiment)',
                        'system': 'Digestive System',
                    },
                ]);

            const patchList = [{ ids: [10210], patch: {'system': 'Digestive Systems'}}, { ids: [10212], patch: {'system': 'Digestive System'}}];
            const expectedActions = [
                { type: types.EP_CREATE_EDIT_OBJECT,
                    object:  {
                        'system': 'Digestive Systems',
                    },
                },
                { type: types.EP_CREATE_EDIT_OBJECT,
                    object: {
                        'system': 'Digestive System',
                    },
                },
                { type: types.EP_PATCH_OBJECTS, ids: [10210] },
                { type: types.EP_PATCH_OBJECTS, ids: [10212] },
                { type: types.EP_RESET_EDIT_OBJECT },
                { type: types.EP_RESET_EDIT_OBJECT },
            ];

            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    ani: 'ani/api/cleanup/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: { active: { id: 57 } },
                endpoint: {
                    items: [
                        {
                            'id': 10210,
                            'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                            'system': 'digestive system',
                        },
                        {
                            'id': 10212,
                            'name': 'gross body weight (start of experiment)',
                            'system': 'systemic',
                        },
                    ],
                    type: 'ani',
                    field: 'system',
                }}, expectedActions, done);
            store.dispatch(endpointActions.patchObjectList(patchList));
        });

    });
});
