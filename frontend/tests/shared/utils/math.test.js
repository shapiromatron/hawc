import {
    addContinuousConfidenceIntervals,
    addDichotomousConfidenceIntervals,
    inv_tdist_05,
} from "shared/utils/math";

import assert from "../../helpers";

describe("shared/utils/math", function () {
    describe("inv_tdist_05", function () {
        it("handles out of bounds", function () {
            assert.ok(isNaN(inv_tdist_05(0)));
            assert.ok(isNaN(inv_tdist_05(351)));
        });
        it("approximated values are close to expected", function () {
            assert.isClose(inv_tdist_05(1), 12.706, 1e-2);
            assert.isClose(inv_tdist_05(2), 4.302, 1e-2);
            assert.isClose(inv_tdist_05(10), 2.228, 1e-2);
            assert.isClose(inv_tdist_05(30), 2.042, 1e-2);
            assert.isClose(inv_tdist_05(250), 1.969, 1e-2);
            assert.isClose(inv_tdist_05(350), 1.969, 1e-2);
        });
    });

    describe("addContinuousConfidenceIntervals", function () {
        it("works with invalid data", function () {
            const endpoint = {
                data: {
                    groups: [
                        {n: undefined, response: 10, stdev: 1},
                        {n: 0, response: 10, stdev: 1},
                        {n: 30, response: undefined, stdev: 1},
                        {n: 30, response: 10, stdev: undefined},
                    ],
                },
            };
            addContinuousConfidenceIntervals(endpoint);
            endpoint.data.groups.forEach(d => {
                assert.ok(d.lower_ci === undefined);
                assert.ok(d.upper_ci === undefined);
            });
        });
        it("works with valid data", function () {
            const endpoint = {
                data: {
                    groups: [
                        {n: 30, response: 10, stdev: 1},
                        {n: 10, response: 10, stdev: 1},
                    ],
                },
            };
            addContinuousConfidenceIntervals(endpoint);

            const lowers = endpoint.data.groups.map(d => d.lower_ci),
                uppers = endpoint.data.groups.map(d => d.upper_ci);

            assert.allClose(lowers, [9.62, 9.28], 0.1);
            assert.allClose(uppers, [10.37, 10.72], 0.1);
        });
    });

    describe("addDichotomousConfidenceIntervals", function () {
        it("works with invalid data", function () {
            const endpoint = {
                data: {
                    groups: [
                        {n: undefined, incidence: 10},
                        {n: 0, incidence: 10},
                        {n: 30, incidence: undefined},
                    ],
                },
            };
            addDichotomousConfidenceIntervals(endpoint);
            endpoint.data.groups.forEach(d => {
                assert.ok(d.lower_ci === undefined);
                assert.ok(d.upper_ci === undefined);
            });
        });
        it("works with valid data", function () {
            const endpoint = {
                data: {
                    groups: [
                        {n: 10, incidence: 0},
                        {n: 10, incidence: 10},
                        {n: 100, incidence: 0},
                        {n: 100, incidence: 100},
                    ],
                },
            };
            addDichotomousConfidenceIntervals(endpoint);

            const lowers = endpoint.data.groups.map(d => d.lower_ci),
                uppers = endpoint.data.groups.map(d => d.upper_ci);

            assert.allClose(lowers, [0.0092, 0.6554, 0.0009, 0.9538], 0.001);
            assert.allClose(uppers, [0.3474, 0.996, 0.0461, 0.9991], 0.001);
        });
    });
});
