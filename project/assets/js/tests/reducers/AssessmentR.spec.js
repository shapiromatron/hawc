import * as types from '../../constants/ActionTypes';
import assessmentReducer from '../../reducers/Assessment';

describe( 'Assessment reducer', () => {

    it('should handle receiving an object', () => {
        expect(assessmentReducer({
            itemsLoaded: false,
            isFetching: false,
            items: [],
        }, {
            type: types.AS_RECEIVE_OBJECT,
            item: {
                "name": "test assessment",
                "id": 0,
                "items": [
                    {
                        "count": 1,
                        "type": "in vitro endpoints",
                        "url": "http://127.0.0.1:9000/in-vitro/api/cleanup/?assessment_id=57",
                    },
                ],
            },
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            items: [{
                "name": "test assessment",
                "id": 0,
                "items": [
                    {
                        "count": 1,
                        "type": "in vitro endpoints",
                        "url": "http://127.0.0.1:9000/in-vitro/api/cleanup/?assessment_id=57",
                    },
                ],
            }],
        });
    });
});
