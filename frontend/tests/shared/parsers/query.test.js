import assert from "assert";
import _ from "lodash";
import {parse} from "shared/parsers/query";

const getValue = i => i,
    negateValue = v => ["NOT", v],
    andValues = (l, r) => ["AND", l, r],
    orValues = (l, r) => ["OR", l, r],
    options = {getValue, negateValue, andValues, orValues};

describe("shared/parsers/query", function () {
    describe("Query", function () {
        it("handles integers, parentheses, AND, OR, and NOT", function () {
            let actual = parse("(1 AND 2) OR NOT 3", options),
                expected = ["OR", ["AND", 1, 2], ["NOT", 3]];
            assert.ok(_.isEqual(actual, expected));
        });
        it("handles case-insensitive input", function () {
            let actual = parse("(1 AND 2) Or not 3", options),
                expected = ["OR", ["AND", 1, 2], ["NOT", 3]];
            assert.ok(_.isEqual(actual, expected));
        });
        it("handles multiple NOTs", function () {
            let actual = parse("NOT NOT 1", options),
                expected = ["NOT", ["NOT", 1]];
            assert.ok(_.isEqual(actual, expected));
        });
        it("maintains order of operations", function () {
            // parentheses has higher priority than AND
            let actual = parse("(1 AND 2) AND (3 AND 4)", options),
                expected = ["AND", ["AND", 1, 2], ["AND", 3, 4]];
            assert.ok(_.isEqual(actual, expected));

            // NOT has higher priority than AND
            actual = parse("NOT 1 AND NOT 2", options);
            expected = ["AND", ["NOT", 1], ["NOT", 2]];
            assert.ok(_.isEqual(actual, expected));

            // AND has higher priority than OR
            actual = parse("1 AND 2 OR 3 AND 4", options);
            expected = ["OR", ["AND", 1, 2], ["AND", 3, 4]];
            assert.ok(_.isEqual(actual, expected));
        });
        it("unable to parse bad strings", function () {
            assert.throws(() => parse("bad string"));
            assert.throws(() => parse("1 2 AND 3"));
            assert.throws(() => parse("(1 AND 2"));
            assert.throws(() => parse("1 AND OR 2"));
        });
    });
});
