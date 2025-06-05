import assert from "assert";
import _ from "lodash";

const isClose = function(actual, expected, atol) {
        return assert.ok(Math.abs(actual - expected) < atol, `|${actual} - ${expected}| > ${atol}`);
    },
    allClose = function(actual, expected, atol) {
        _.zip(actual, expected).map(d => {
            isClose(d[0], d[1], atol);
        });
    };

assert.isClose = isClose;
assert.allClose = allClose;

// This file only provides helpers for other test files and does not need to be run as a test suite itself.
// Remove this file from test matching or rename to helpers-util.js if you want to avoid Vitest trying to run it as a test.

export default assert;
