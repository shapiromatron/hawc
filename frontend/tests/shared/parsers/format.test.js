import assert from "assert";
import Format from "shared/parsers/format";

const obj = {one: 1, two: 2},
    getValue = prop => obj[prop],
    options = {getValue};

describe("shared/parsers/format", function() {
    describe("Format", function() {
        it("handles a substitute", function() {
            let actual = Format.parse("${one}", options),
                expected = "1";
            assert.ok(actual == expected);
        });
        it("handles multiple substitutes", function() {
            let actual = Format.parse("${one} and ${two}", options),
                expected = "1 and 2";
            assert.ok(actual == expected);
        });
        it("handles no substitutes", function() {
            let actual = Format.parse("No numbers!", options),
                expected = "No numbers!";
            assert.ok(actual == expected);
        });
        it("handles leading and trailing literals", function() {
            let actual = Format.parse("1 + ${one} = 2", options),
                expected = "1 + 1 = 2";
            assert.ok(actual == expected);
        });
        it("unable to parse bad strings", function() {
            // substitutions need to be closed
            assert.throws(() => Format.parse("${identifier"));
            // the identifier must only consist of alphanumeric characters,
            // spaces, hyphens, or underscores
            assert.throws(() => Format.parse("${inv@lid}"));
        });
    });
});
