import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import nock from 'nock';

import * as assessmentActions from 'textCleanup/actions/Assessment';
import * as types from 'textCleanup/constants/ActionTypes';

import { HOST } from 'tests/constants';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('textCleanup Assessment actions', () => {
    afterEach(() => {
        nock.cleanAll();
    });

    describe('async actions', () => {
        it('should create an action to load an assessment', (done) => {
            nock(HOST)
                .get('/assessment/api/endpoints/?assessment_id=57')
                .reply(200, {
                    name: 'test assessment',
                    id: 57,
                    items: [
                        {
                            count: 1,
                        },
                    ],
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                {
                    type: types.AS_RECEIVE_OBJECT,
                    item: {
                        name: 'test assessment',
                        id: 57,
                        items: [
                            {
                                count: 1,
                            },
                        ],
                    },
                },
            ];
            const store = mockStore(
                {
                    config: {
                        host: HOST,
                        assessment_id: '57',
                        assessment: 'assessment/api/endpoints/',
                    },
                    assessment: {},
                },
                expectedActions,
                done
            );
            store.dispatch(assessmentActions.fetchObjectIfNeeded(57));
        });

        it('should be able to make an assessment active', (done) => {
            nock(HOST)
                .get('/assessment/api/endpoints/?assessment_id=57')
                .reply(200, {
                    name: 'test assessment',
                    id: 57,
                    items: [
                        {
                            count: 1,
                        },
                    ],
                });

            const expectedActions = [
                { type: types.AS_REQUEST },
                {
                    type: types.AS_RECEIVE_OBJECT,
                    item: {
                        name: 'test assessment',
                        id: 57,
                        items: [
                            {
                                count: 1,
                            },
                        ],
                    },
                },
                {
                    type: types.AS_SELECT,
                    object: {
                        name: 'test assessment',
                        id: 57,
                        items: [
                            {
                                count: 1,
                            },
                        ],
                    },
                },
            ];
            const store = mockStore(
                {
                    config: {
                        host: HOST,
                        assessment_id: '57',
                        assessment: 'assessment/api/endpoints/',
                    },
                    assessment: {},
                },
                expectedActions,
                done
            );
            store.dispatch(assessmentActions.makeAssessmentActive(57));
        });
    });
});
