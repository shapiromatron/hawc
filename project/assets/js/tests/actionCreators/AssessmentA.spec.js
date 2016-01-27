import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as assessmentActions from '../../actions/Assessment';
import * as types from '../../constants/ActionTypes';
import nock from 'nock';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('Assessment actions', () => {
    afterEach(() => {
        nock.cleanAll();
    });

    describe('actions', () => {

        it('should be able to select an assessment', () => {
            let action = assessmentActions.selectObject(0);

            expect(action).to.deep.equal({
                type: types.AS_SELECT,
                id: 0,
            });
        })
    })

    describe('async actions', () => {

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
});
