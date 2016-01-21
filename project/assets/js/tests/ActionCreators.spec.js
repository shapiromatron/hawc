import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import * as actions from '../actions/Assessment';
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

    it('create an action to load an assessment', (done) => {
        nock('http://127.0.0.1:9000')
            .get('/assessment/api/endpoints/?assessment_id=57')
            .reply(200, {
                "name": "PFOA/PFOS Exposure and Immunotoxicity",
                "id": 57,
                "items": [
                    {
                        "count": 2915,
                        "type": "animal bioassay endpoints",
                        "url": "http://127.0.0.1:9000/ani/api/cleanup/?assessment_id=57"
                    },
                    {
                        "count": 334,
                        "type": "epidemiological outcomes assessed",
                        "url": "http://127.0.0.1:9000/epi/api/cleanup/?assessment_id=57"
                    },
                    {
                        "count": 0,
                        "type": "in vitro endpoints",
                        "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57"
                    },
                ]
            });

        const expectedActions = [
            { type: types.AS_REQUEST },
            { type: types.AS_SUCCESS, item: {
                "name": "PFOA/PFOS Exposure and Immunotoxicity",
                "id": 57,
                "items": [
                    {
                        "count": 2915,
                        "type": "animal bioassay endpoints",
                        "url": "http://127.0.0.1:9000/ani/api/cleanup/?assessment_id=57"
                    },
                    {
                        "count": 334,
                        "type": "epidemiological outcomes assessed",
                        "url": "http://127.0.0.1:9000/epi/api/cleanup/?assessment_id=57"
                    },
                    {
                        "count": 0,
                        "type": "in vitro endpoints",
                        "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57"
                    },
                ]
            } },
        ];
        const store = mockStore({ apiUrl: 'http://127.0.0.1:9000', config: { assessment: 'assessment/api/endpoints/'}, assessment: {} }, expectedActions, done);
        store.dispatch(actions.fetchObjectIfNeeded(57));
    });
})
