import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import nock from 'nock';

import { HOST } from 'tests/constants';

import * as filterActions from 'riskofbias/robVisual/actions/Filter';
import * as types from 'riskofbias/robVisual/constants/ActionTypes';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('robVisual Filter actions', () => {
    describe('async actions', () => {
        afterEach(() => {
            nock.cleanAll();
        });

        it('should load endpoint effects', (done) => {
            nock(HOST)
                .get('/ani/api/endpoint/effects/?assessment_id=126')
                .reply(200, [
                    'anxiety/motor activity',
                    'depression/motor endurance',
                    'development:ear opening',
                    'development:eye opening',
                ]);

            const expectedActions = [
                { type: types.REQUEST_EFFECTS },
                {
                    type: types.RECEIVE_EFFECTS,
                    effects: [
                        'anxiety/motor activity',
                        'depression/motor endurance',
                        'development:ear opening',
                        'development:eye opening',
                    ],
                },
            ];

            const store = mockStore(
                {
                    config: {
                        host: HOST,
                        assessment_id: '126',
                        endpoint_effect_url:
                            'ani/api/endpoint/effects/?assessment_id=126',
                    },
                },
                expectedActions,
                done
            );

            store.dispatch(filterActions.fetchEffects());
        });

        it('should load RoB scores', (done) => {
            nock(HOST)
                .get('/study/api/study/rob_scores/?assessment_id=126')
                .reply(200, [
                    {
                        short_citation: 'Reddy and Karnati, 2015',
                        id: 97857,
                        final_score: null,
                    },
                    {
                        short_citation: 'Rumiantsev et al. 1988',
                        id: 52541,
                        final_score: 19,
                    },
                    {
                        short_citation: 'Shen et al., 2004',
                        id: 57040,
                        final_score: 25,
                    },
                ]);

            const expectedActions = [
                { type: types.REQUEST_ROB_SCORES },
                {
                    type: types.RECEIVE_ROB_SCORES,
                    robScores: [
                        {
                            short_citation: 'Reddy and Karnati, 2015',
                            id: 97857,
                            final_score: null,
                        },
                        {
                            short_citation: 'Rumiantsev et al. 1988',
                            id: 52541,
                            final_score: 19,
                        },
                        {
                            short_citation: 'Shen et al., 2004',
                            id: 57040,
                            final_score: 25,
                        },
                    ],
                },
            ];

            const store = mockStore(
                {
                    config: {
                        host: HOST,
                        study_score_url:
                            'study/api/study/rob_scores/?assessment_id=126',
                    },
                },
                expectedActions,
                done
            );

            store.dispatch(filterActions.fetchRobScores());
        });

        it('should load endpoints', (done) => {
            nock(HOST)
                .get(
                    '/ani/api/endpoint/rob_filter/?assessment_id=126&study_id[]=8199,8200&effect[]=general%20behavior'
                )
                .reply(200, [
                    {
                        id: 8199,
                        assessment: 126,
                        effects: [
                            {
                                slug: 'general-behavior',
                                name: 'general behavior',
                            },
                        ],
                    },
                    {
                        id: 8200,
                        assessment: 126,
                        effects: [
                            {
                                slug: 'general-behavior',
                                name: 'general behavior',
                            },
                        ],
                    },
                ]);

            const expectedActions = [
                { type: types.REQUEST_ENDPOINTS },
                {
                    type: types.RECEIVE_ENDPOINTS,
                    endpoints: [
                        {
                            id: 8199,
                            assessment: 126,
                            effects: [
                                {
                                    slug: 'general-behavior',
                                    name: 'general behavior',
                                },
                            ],
                        },
                        {
                            id: 8200,
                            assessment: 126,
                            effects: [
                                {
                                    slug: 'general-behavior',
                                    name: 'general behavior',
                                },
                            ],
                        },
                    ],
                },
            ];

            const store = mockStore(
                {
                    config: {
                        host: HOST,
                        endpoint_filter_url:
                            'ani/api/endpoint/rob_filter/?assessment_id=126',
                    },
                    filter: { selectedEffects: ['general behavior'] },
                },
                expectedActions,
                done
            );

            store.dispatch(filterActions.fetchEndpoints([8199, 8200]));
        });
    });
});
