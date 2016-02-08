import * as types from 'constants/ActionTypes';
import endpointReducer from 'reducers/Endpoint';

describe('Endpoint reducer', () => {

    it('should handle receiving the Endpoint model', () => {
        expect(endpointReducer({
            itemsLoaded: false,
            isFetching: false,
            model: null,
            type: null,
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        }, {
            type: types.EP_RECEIVE_MODEL,
            model: {
                'text_cleanup_fields': [
                    'system',
                    'organ',
                    'effect',
                    'effect_subtype',
                ],
            },
        })).to.deep.equal({
            itemsLoaded: false,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: null,
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        });
    });

    it('should handle setting the Endpoint field', () => {
        expect(endpointReducer({
            itemsLoaded: false,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: null,
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        }, {
            type: types.EP_SET_FIELD,
            field: 'system',
        })).to.deep.equal({
            itemsLoaded: false,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: null,
            field: 'system',
            items: [],
            editObject: {},
            editObjectErrors: {},
        });
    });

    it('should handle setting the Endpoint type', () => {
        expect(endpointReducer({
            itemsLoaded: false,
            isFetching: true,
            model: null,
            type: null,
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        }, {
            type: types.EP_SET_TYPE,
            endpoint_type: 'ani',

        })).to.deep.equal({
            itemsLoaded: false,
            isFetching: false,
            model: null,
            type: 'ani',
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        });
    });

    it('should create an edit object', () => {
        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'digestive system',
                },
            ],
            editObject: null,
            editObjectErrors: {},
        }, {
            type: types.EP_CREATE_EDIT_OBJECT,
            object: {
                'field': 'system',
                'system': 'digestive system',
                'ids': [10210, 10212],
            },
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'digestive system',
                },
            ],
            editObject: {
                'digestive system': {
                    'field': 'system',
                    'system': 'digestive system',
                    'ids': [10210, 10212],
                },
            },
            editObjectErrors: {},
        });
    });

    it('should be able to patch multiple objects', () => {
        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'digestive system',
                },
                {
                    'id': 10212,
                    'name': 'gross body weight (start of experiment)',
                    'system': 'systemic',
                },
            ],
            editObject: {'system': 'Digestive Systems'},
            editObjectErrors: {},
        }, {
            type: types.EP_PATCH_OBJECTS,
            ids: [10210, 10212],
            patch: {'system': 'Digestive Systems'},
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            field: 'system',
            type: 'ani',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'Digestive Systems',
                },
                {
                    'id': 10212,
                    'name': 'gross body weight (start of experiment)',
                    'system': 'Digestive Systems',
                },
            ],
            editObject: {'system': 'Digestive Systems'},
            editObjectErrors: {},
        });
    });

    it('should handle deleting an object', () => {

        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'digestive system',
                },
                {
                    'id': 10212,
                    'name': 'gross body weight (start of experiment)',
                    'system': 'systemic',
                },
            ],
            editObject: {'system': 'Digestive Systems'},
            editObjectErrors: {},
        }, {
            type: types.EP_DELETE_OBJECT,
            id: 10210,
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10212,
                    'name': 'gross body weight (start of experiment)',
                    'system': 'systemic',
                },
            ],
            editObject: {'system': 'Digestive Systems'},
            editObjectErrors: {},
        });
    });

    it('should revert to default state upon release', () => {
        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            type: 'ani',
            field: 'system',
            items: [
                {
                    'id': 10210,
                    'name': 'biliary total bile acid/phospholipid (BA/PL) ratio in liver',
                    'system': 'digestive system',
                },
                {
                    'id': 10212,
                    'name': 'gross body weight (start of experiment)',
                    'system': 'systemic',
                },
            ],
            editObject: {'system': 'Digestive Systems'},
            editObjectErrors: {},
        }, {
            type: types.EP_RELEASE,
        })).to.deep.equal({
            itemsLoaded: false,
            isFetching: false,
            model: null,
            type: null,
            field: null,
            items: [],
            editObject: {},
            editObjectErrors: {},
        });
    });
});
