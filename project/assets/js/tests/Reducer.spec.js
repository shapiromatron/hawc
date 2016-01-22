import { expect } from 'chai';
import * as types from '../constants/ActionTypes';
import rootReducer from '../reducers';
import assessmentReducer from '../reducers/Assessment';
import endpointReducer from '../reducers/Endpoint';

describe('rootReducer', () => {
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
                items: [],
                editObject: null,
                editObjectErrors: {},
            },
            config: {},
            router: null,
        });
    });
});

describe( 'assessmentReducer', () => {

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
                        "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57",
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
                        "url": "http://127.0.0.1:9000/invitro/api/cleanup/?assessment_id=57",
                    },
                ],
            }],
        });
    });

    it('should handle deleting an object', () => {

        expect(assessmentReducer({
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
        }, {
            type: types.AS_DELETE_OBJECT,
            id: 0,
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            items: [],
        });
    });

});

describe('endpointReducer', () => {

    it('should handle receiving the Endpoint model', () => {
        expect(endpointReducer({
            itemsLoaded: false,
            isFetching: false,
            model: null,
            type: null,
            items: [],
            editObject: null,
            editObjectErrors: {},
        }, {
            type: types.EP_RECEIVE_MODEL,
            model: {
                "text_cleanup_fields": [
                    "system",
                    "organ",
                    "effect",
                    "effect_subtype",
                ],
            },
        })).to.deep.equal({
            itemsLoaded: false,
            isFetching: false,
            model: [
                "system",
                "organ",
                "effect",
                "effect_subtype",
            ],
            type: null,
            items: [],
            editObject: null,
            editObjectErrors: {},
        });
    });

    it('should create an edit object', () => {
        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                "system",
                "organ",
                "effect",
                "effect_subtype",
            ],
            type: "system",
            items: [
                {
                    "id": 10210,
                    "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                    "system": "digestive system",
                },
            ],
            editObject: null,
            editObjectErrors: {},
        }, {
            type: types.EP_CREATE_EDIT_OBJECT,
            object: {
                "system": "digestive system",
            },
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            model: [
                "system",
                "organ",
                "effect",
                "effect_subtype",
            ],
            type: "system",
            items: [
                {
                    "id": 10210,
                    "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                    "system": "digestive system",
                },
            ],
            editObject: {"system": "digestive system"},
            editObjectErrors: {},
        });
    });

    it('should be able to patch multiple objects', () => {
        expect(endpointReducer({
            itemsLoaded: true,
            isFetching: false,
            model: [
                "system",
                "organ",
                "effect",
                "effect_subtype",
            ],
            type: "system",
            items: [
                {
                    "id": 10210,
                    "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                    "system": "digestive system",
                },
                {
                    "id": 10212,
                    "name": "gross body weight (start of experiment)",
                    "system": "systemic",
                },
            ],
            editObject: {"system": "Digestive Systems"},
            editObjectErrors: {},
        }, {
            type: types.EP_PATCH_OBJECTS,
            ids: [10210, 10212],
        })).to.deep.equal({
            itemsLoaded: true,
            isFetching: false,
            model: [
                "system",
                "organ",
                "effect",
                "effect_subtype",
            ],
            type: "system",
            items: [
                {
                    "id": 10210,
                    "name": "biliary total bile acid/phospholipid (BA/PL) ratio in liver",
                    "system": "Digestive Systems",
                },
                {
                    "id": 10212,
                    "name": "gross body weight (start of experiment)",
                    "system": "Digestive Systems",
                },
            ],
            editObject: {"system": "Digestive Systems"},
            editObjectErrors: {},
        });
    });
});
