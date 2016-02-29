import * as types from 'constants/ActionTypes';
import assessmentReducer from 'reducers/Assessment';

describe('textCleanup Assessment reducer', () => {

    it('should handle receiving an object', () => {
        expect(assessmentReducer({
            itemsLoaded: false,
            isFetching: true,
            items: [],
        }, {
            type: types.AS_RECEIVE_OBJECT,
            item: {
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            },
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            items: [{
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            }],
        });
    });

    it('should handle an assessment selection', () => {
        expect(assessmentReducer({
            active: null,
            items: [{
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            }],
        }, {
            type: types.AS_SELECT,
            object: {
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            },
        })).to.deep.equal({
            active: {
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            },
            items: [{
                'name': 'test assessment',
                'id': 0,
                'items': [
                    {
                        'count': 1,
                        'title': 'in vitro endpoints',
                        'type': 'iv',
                    },
                ],
            }],
        });
    });
});
