import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as filterActions from 'robVisual/actions/Filter';
import * as types from 'robVisual/constants/ActionTypes';
import nock from 'nock';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('robVisual Filter actions', () => {
    // describe('actions', () => {
    //
    // });

    describe('async actions', () => {
        afterEach(() => {
            nock.cleanAll();
        });

        it('should load endpoint effects', (done) => {
            nock('http://127.0.0.1:9000')
                .get('/ani/api/endpoint/effects/?assessment_id=126')
                .reply(200, [
                    'anxiety/motor activity',
                    'depression/motor endurance',
                    'development:ear opening',
                    'development:eye opening',
                ]);

            const expectedActions = [
                { type: types.REQUEST_EFFECTS },
                { type: types.RECEIVE_EFFECTS, effects: [
                    'anxiety/motor activity',
                    'depression/motor endurance',
                    'development:ear opening',
                    'development:eye opening',
                ]},
            ];

            const store = mockStore({
                config: {
                    apiUrl: 'http://127.0.0.1:9000',
                    assessment_id: '126',
                    endpoint_effect_url: '/ani/api/endpoint/effects/?assessment_id=126',
                },
            }, expectedActions, done);

            store.dispatch(filterActions.fetchEffects());
        });
    });
});
