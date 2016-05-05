import * as types from 'textCleanup/constants/ActionTypes';
import rootReducer from 'textCleanup/reducers';


describe('textCleanup Root reducer', () => {
    it('should return initial state', () => {
        expect(rootReducer(undefined, {})).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: false,
                active: null,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                model: null,
                items: [],
                editObject: {},
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });

    it('should handle an Assessment action', () => {
        expect(rootReducer(undefined, {
            type: types.AS_REQUEST,
        })).to.deep.equal({
            assessment: {
                itemsLoaded: false,
                isFetching: true,
                active: null,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: false,
                model: null,
                items: [],
                editObject: {},
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
                active: null,
                items: [],
            },
            endpoint: {
                itemsLoaded: false,
                isFetching: true,
                model: null,
                items: [],
                editObject: {},
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });
});
