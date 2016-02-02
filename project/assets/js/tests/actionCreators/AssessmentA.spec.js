import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as assessmentActions from 'actions/Assessment';
import * as types from 'constants/ActionTypes';
import nock from 'nock';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('Assessment actions', () => {
    afterEach(() => {
        nock.cleanAll();
    });

    describe('async actions', () => {

        it('should create an action to load an assessment', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/assessment/api/endpoints/?assessment_id=57')
                .reply(200, {
                    'name': 'test assessment',
                    'id': 57,
                    'items': [
                        {
                            'count': 1,
                        },
                    ],
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                { type: types.AS_RECEIVE_OBJECT, item: {
                    'name': 'test assessment',
                    'id': 57,
                    'items': [
                        {
                            'count': 1,
                        },
                    ],
                } },
            ];
            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    assessment_id: '57',
                    assessment: 'assessment/api/endpoints/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: {} }, expectedActions, done);
            store.dispatch(assessmentActions.fetchObjectIfNeeded(57));
        });

        it('should be able to make an assessment active', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/assessment/api/endpoints/?assessment_id=57')
                .reply(200, {
                    'name': 'test assessment',
                    'id': 57,
                    'items': [
                        {
                            'count': 1,
                        },
                    ],
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                { type: types.AS_RECEIVE_OBJECT, item: {
                    'name': 'test assessment',
                    'id': 57,
                    'items': [
                        {
                            'count': 1,
                        },
                    ],
                }},
                {type: types.AS_SELECT, object: {
                    'name': 'test assessment',
                    'id': 57,
                    'items': [
                        {
                            'count': 1,
                        },
                    ],
                }},
            ];
            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000/',
                    assessment_id: '57',
                    assessment: 'assessment/api/endpoints/',
                    csrf: '<input type="hidden" name="csrfmiddlewaretoken" value="SMrZbPkbRwKxWOhwrIGsmRDMFqgULnWn" />',
                },
                assessment: {} }, expectedActions, done);
            store.dispatch(assessmentActions.makeAssessmentActive(57));
        });

    });
});
