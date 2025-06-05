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

export default assert;
