import {NULL_VALUE} from "../../summary/constants";

const defineProps = function (id, label, column) {
        return {id, label, column};
    },
    defineAxis = function (field, opts) {
        opts = opts || {};
        return {
            id: field.id,
            label: field.label,
            settings: [
                {column: field.column, items: null, delimiter: opts.delimiter || "", wrap_text: 0},
            ],
        };
    },
    defineMultiAxis = function (fields, id, label, opts) {
        opts = opts || {};
        return {
            id,
            label,
            settings: fields.map(field => {
                return {
                    column: field.column,
                    items: null,
                    delimiter: opts.delimiter || "",
                    wrap_text: 0,
                };
            }),
        };
    },
    defineFilter = function (field, opts) {
        opts = opts || {};
        return {
            id: field.id,
            label: field.label,
            settings: {
                column: field.column,
                delimiter: opts.delimiter || "",
                on_click_event: opts.on_click_event || NULL_VALUE,
            },
        };
    },
    defineTable = function (field, opts) {
        opts = opts || {};
        return {
            id: field.id,
            label: field.label,
            settings: {
                column: field.column,
                delimiter: opts.delimiter || "",
                on_click_event: opts.on_click_event || NULL_VALUE,
            },
        };
    },
    COLORS = {
        black: "#000000",
        blue: "#2339a9",
        green: "#006570",
        orange: "#b35b0b",
        purple: "#47378b",
        red: "#66002b",
    };

export {COLORS, defineAxis, defineFilter, defineMultiAxis, defineProps, defineTable};
