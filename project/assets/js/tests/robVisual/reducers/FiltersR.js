import * as types from 'robVisual/constants/ActionTypes';
import filterReducer from 'robVisual/reducers/Filter';

describe('robVisual Filter reducer', () => {

    it('should handle requesting effects', () => {
        expect(filterReducer({
            effects: [],
            isFetchingEffects: false,
        }, { type: types.REQUEST_EFFECTS })).to.deep.equal({
            effects: [],
            isFetchingEffects: true,
        });
    });

    it('should handle requesting endpoints', () => {
        expect(filterReducer({
            endpoints: [],
            isFetchingEndpoints: false,
        }, { type: types.REQUEST_ENDPOINTS })).to.deep.equal({
            endpoints: [],
            isFetchingEndpoints: true,
        });
    });

    it('should handle requesting Rob scores', () => {
        expect(filterReducer({
            robScores: [],
            isFetchingRobScores: false,
        }, { type: types.REQUEST_ROB_SCORES })).to.deep.equal({
            robScores: [],
            isFetchingRobScores: true,
        });
    });

    it('should handle receiving effects', () => {
        expect(filterReducer({
            effects: [],
            isFetchingEffects: true,
        }, {
            type: types.RECEIVE_EFFECTS,
            effects: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
        })).to.deep.equal({
            effects: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
            isFetchingEffects: false,
        });
    });

    it('should handle receiving endpoints', () => {
        expect(filterReducer({
            endpoints: [],
            isFetchingEndpoints: true,
        }, {
            type: types.RECEIVE_ENDPOINTS,
            endpoints: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
        })).to.deep.equal({
            endpoints: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
            isFetchingEndpoints: false,
            endpointsLoaded: true,
        });
    });

    it('should handle receiving robScores', () => {
        expect(filterReducer({
            robScores: [],
            isFetchingRobScores: true,
        }, {
            type: types.RECEIVE_ROB_SCORES,
            robScores: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
        })).to.deep.equal({
            robScores: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
            isFetchingRobScores: false,
        });
    });

    it('should handle selecting effects', () => {
        expect(filterReducer({
            effects: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
            selectedEffects: null,
        }, {
            type: types.SELECT_EFFECTS,
            effects: 'anxiety/motor activity',
        })).to.deep.equal({
            effects: [
                'anxiety/motor activity',
                'depression/motor endurance',
                'development:ear opening',
            ],
            selectedEffects: 'anxiety/motor activity',
        });
    });

    it('should handle setting the RoB score threshold', () => {
        expect(filterReducer({
            robScoreThreshold: null,
        }, {
            type: types.SET_ROB_THRESHOLD,
            threshold: 30,
        })).to.deep.equal({
            robScoreThreshold: 30,
        });
    });
});
