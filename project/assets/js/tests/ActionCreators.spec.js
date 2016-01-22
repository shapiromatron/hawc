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
        nock.cleanAll()
    })

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
                            "type": "in vitro endpoints",
                            "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57"
                        },
                    ]
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                { type: types.AS_SUCCESS, item: {
                    "name": "test assessment",
                    "id": 57,
                    "items": [
                        {
                            "count": 1,
                            "type": "in vitro endpoints",
                            "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57"
                        },
                    ]
                } },
            ];
            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    assessment: "assessment/api/endpoints/",
                    epi_cleanup: "epi/api/cleanup/",
                    animal_cleanup: "ani/api/cleanup/",
                    iv_cleanup: "in-vitro/api/cleanup/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: {} }, expectedActions, done);
            store.dispatch(assessmentActions.fetchObjectIfNeeded(57));
        });
    });

    describe('Endpoint actions', () => {

        it('should delete an object', (done) => {
            nock('http://127.0.0.1:9000')
                .delete('/epi/api/cleanup/?assessment_id=57')
                .reply(200, {});

            const expectedActions = [
                { type: types.AS_DELETE_OBJECT, id: 57 }
            ]
            const store = mockStore({
                apiUrl: 'http://127.0.0.1:9000',
                config: {
                    assessment: "assessment/api/endpoints/",
                    epi_cleanup: "epi/api/cleanup/",
                    animal_cleanup: "ani/api/cleanup/",
                    iv_cleanup: "in-vitro/api/cleanup/",
                    csrf: "<input type='hidden' name='csrfmiddlewaretoken' value='SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn' />",
                },
                assessment: {} }, expectedActions, done);
            store.dispatch(endpointActions.deleteObject(57));
        })

    })
});
