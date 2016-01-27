import { expect } from 'chai';
import * as types from '../../constants/ActionTypes';
import rootReducer from '../../reducers';

describe('Root reducer', () => {
    it('should return initial state', () => {
        expect(rootReducer(undefined, {})).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                model: null,
                type: null,
                field: null,
                items: [],
                editObject: null,
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });

    it('should handle an Assessment action', () => {
        expect(rootReducer({}, {
            type: types.AS_REQUEST,
        })).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: true,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                model: null,
                type: null,
                field: null,
                items: [],
                editObject: null,
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });

    it('should handle an Endpoint action', () => {
        expect(rootReducer(undefined, {
            type: types.EP_REQUEST,
        })).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: false,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: true,
                model: null,
                type: null,
                field: null,
                items: [],
                editObject: null,
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });
});
