import * as types from 'constants/ActionTypes';
import endpointReducer from 'reducers/Endpoint';

describe('textCleanup Endpoint reducer', () => {

    it('should handle receiving the Endpoint model', () => {
        expect(endpointReducer({
            isFetching: true,
            model: null,
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
            isFetching: false,
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
        });
    });

    it('should handle setting the Endpoint field', () => {
        expect(endpointReducer({
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            field: null,
        }, {
            type: types.EP_SET_FIELD,
            field: 'system',
        })).to.deep.equal({
            model: [
                'system',
                'organ',
                'effect',
                'effect_subtype',
            ],
            field: 'system',
        });
    });

    it('should handle setting the Endpoint type', () => {
        expect(endpointReducer({
            isFetching: true,
            type: null,
        }, {
            type: types.EP_SET_TYPE,
            endpoint_type: 'ani',

        })).to.deep.equal({
            isFetching: false,
            type: 'ani',
            items: [],
        });
    });

    it('should create an edit object', () => {
        expect(endpointReducer({
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
        }, {
            type: types.EP_CREATE_EDIT_OBJECT,
            object: {
                'field': 'system',
                'system': 'digestive system',
                'ids': [10210, 10212],
            },
        })).to.deep.equal({
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
            isFetching: false,
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
