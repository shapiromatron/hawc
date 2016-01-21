import { expect } from 'chai';
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
        })
    })
})
