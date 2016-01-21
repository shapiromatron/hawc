import { expect } from 'chai';
import * as types from '../constants/ActionTypes';
import rootReducer from '../reducers';

describe('rootReducer', () => {
    it('should return initial state', () => {
        expect(rootReducer(undefined, {})).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            config: {},
            router: null,
        });
    });

    it('should handle a request', () => {
        expect(rootReducer({}, {
            type: types.AS_REQUEST,
        })).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: true,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            config: {},
            router: null,
        });
    });

    it('should handle receiving an object', () => {
        expect(rootReducer({}, {
            type: types.AS_RECEIVE_OBJECT,
            item: {
                "name": "test assessment",
                "id": 0,
                "items": [
                    {
                        "count": 1,
                        "type": "in vitro endpoints",
                        "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57",
                    },
                ],
            },
        })).to.deep.equal({
            assessment: {
                itemsLoaded: true,
                isFetching: false,
                items: [{
                    "name": "test assessment",
                    "id": 0,
                    "items": [
                        {
                            "count": 1,
                            "type": "in vitro endpoints",
                            "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57",
                        },
                    ],
                }],
                editObject: null,
                editObjectErrors: null,
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            config: {},
            router: null,
        });
    });

    it('should handle deleting an object', () => {

        expect(rootReducer({
            assessment: {
                itemsLoaded: true,
                isFetching: false,
                items: [{
                    "name": "test assessment",
                    "id": 0,
                    "items": [
                        {
                            "count": 1,
                            "type": "in vitro endpoints",
                            "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57",
                        },
                    ],
                }],
                editObject: null,
                editObjectErrors: null,
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            config: {},
            router: null,
        }, {
            type: types.AS_DELETE_OBJECT,
            id: 0,
        })).to.deep.equal({
            assessment: {
                itemsLoaded: true,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
                editObject: null,
                editObjectErrors: null,
            },
            config: {},
            router: null,
        });
    });

    it('should be able to edit an object')

});
