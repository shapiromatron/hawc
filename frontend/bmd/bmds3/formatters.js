// original source of this file:
// https://github.com/USEPA/BMDS-UI/blob/001261919d030daf2f1994e3430cc0d63bc2e371/frontend/src/utils/formatters.js

import _ from "lodash";

const BMDS_BLANK_VALUE = -9999;
const ff = function(value) {
        // ff = float format
        if (value === 0) {
            return value.toString();
        } else if (value == BMDS_BLANK_VALUE || !_.isFinite(value)) {
            return "-";
        } else if (Math.abs(value) > 0.001 && Math.abs(value) < 1e5) {
            // local print "0" for anything smaller than this
            return value.toLocaleString();
        } else {
            // too many 0; use exponential notation
            return value.toExponential(2);
        }
    },
    parameterFormatter = function(value) {
        if (value === 0) {
            return value.toString();
        } else if (value == BMDS_BLANK_VALUE || !_.isFinite(value)) {
            return "-";
        } else if (Math.abs(value) >= 1000 || Math.abs(value) <= 0.001) {
            return value.toExponential(3);
        } else {
            return value.toPrecision(4);
        }
    },
    fractionalFormatter = function(value) {
        // Expected values between 0 and 1
        if (value == BMDS_BLANK_VALUE || !_.isFinite(value) || value < 0) {
            return "-";
        } else if (value === 0) {
            return value.toString();
        } else if (value < 0.0001) {
            return "< 0.0001";
        } else {
            return value.toPrecision(3);
        }
    };

export {ff, fractionalFormatter, parameterFormatter};
