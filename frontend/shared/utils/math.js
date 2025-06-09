import _ from "lodash";

const gcf = function (X, A) {
        // Good for X>A+1
        var A0 = 0,
            B0 = 1,
            A1 = 1,
            B1 = X,
            AOLD = 0,
            N = 0;
        while (Math.abs((A1 - AOLD) / A1) > 0.00001) {
            AOLD = A1;
            N = N + 1;
            A0 = A1 + (N - A) * A0;
            B0 = B1 + (N - A) * B0;
            A1 = X * A0 + N * A1;
            B1 = X * B0 + N * B1;
            A0 = A0 / B1;
            B0 = B0 / B1;
            A1 = A1 / B1;
            B1 = 1;
        }
        var Prob = Math.exp(A * Math.log(X) - X - logGamma(A)) * A1;
        return 1 - Prob;
    },
    gser = function (X, A) {
        // Good for X<A+1
        var T9 = 1 / A,
            G = T9,
            I = 1;
        while (T9 > G * 0.00001) {
            T9 = (T9 * X) / (A + I);
            G = G + T9;
            I = I + 1;
        }
        G = G * Math.exp(A * Math.log(X) - X - logGamma(A));
        return G;
    },
    logGamma = function (Z) {
        var S =
                1 +
                76.18009173 / Z -
                86.50532033 / (Z + 1) +
                24.01409822 / (Z + 2) -
                1.231739516 / (Z + 3) +
                0.00120858003 / (Z + 4) -
                0.00000536382 / (Z + 5),
            LG = (Z - 0.5) * Math.log(Z + 4.5) - (Z + 4.5) + Math.log(S * 2.50662827465);
        return LG;
    },
    normalCDF = function (X) {
        // cumulative density function (CDF) for the standard normal distribution
        // HASTINGS.  MAX ERROR = .000001
        var T = 1 / (1 + 0.2316419 * Math.abs(X)),
            D = 0.3989423 * Math.exp((-X * X) / 2),
            p =
                D *
                T *
                (0.3193815 + T * (-0.3565638 + T * (1.781478 + T * (-1.821256 + T * 1.330274))));
        return X > 0 ? 1 - p : p;
    },
    gammaCDF = function (x, a) {
        // adapted from http://www.math.ucla.edu/~tom/distributions/gamma.html
        if (x <= 0) {
            return 0;
        } else if (a > 200) {
            var z = (x - a) / Math.sqrt(a);
            var y = normalCDF(z);
            var b1 = 2 / Math.sqrt(a);
            var phiz = 0.39894228 * Math.exp((-z * z) / 2);
            var w = y - (b1 * (z * z - 1) * phiz) / 6; // Edgeworth1
            var b2 = 6 / a;
            var u = 3 * b2 * (z * z - 3) + b1 * b1 * (z ^ (4 - 10 * z * z + 15));
            return w - (phiz * z * u) / 72; // Edgeworth2
        } else if (x < a + 1) {
            return gser(x, a);
        } else {
            return gcf(x, a);
        }
    },
    inv_tdist_05 = function (df) {
        // Calculates the inverse t-distribution using a piecewise linear form for
        // the degrees of freedom specified. Assumes a two-tailed distribution with
        // an alpha of 0.05. Based on curve-fitting using Excel's T.INV.2T function
        // with a maximum absolute error of 0.00924 and percent error of 0.33%.
        //
        // Roughly equivalent to scipy.stats.t.ppf(0.975, df)
        var b;
        if (df < 1) {
            return NaN;
        } else if (df == 1) {
            return 12.7062047361747;
        } else if (df < 12) {
            b = [
                7.9703237683e-5, -3.5145890027e-3, 0.063259191874, -0.5963723075, 3.129413441,
                -8.8538894383, 13.358101926,
            ];
        } else if (df < 62) {
            b = [
                1.1184055716e-10, -2.7885328039e-8, 2.8618499662e-6, -1.5585120701e-4,
                4.8300645273e-3, -0.084316656676, 2.7109288893,
            ];
        } else {
            b = [
                5.1474329765e-16, -7.262226388e-13, 4.2142967681e-10, -1.2973354626e-7,
                2.275308052e-5, -2.2594979441e-3, 2.0766977669,
            ];
            if (df > 350) {
                console.warn("Extrapolating beyond inv_tdist_05 regression range (N>350).");
                return NaN;
            }
        }
        return (
            b[0] * Math.pow(df, 6) +
            b[1] * Math.pow(df, 5) +
            b[2] * Math.pow(df, 4) +
            b[3] * Math.pow(df, 3) +
            b[4] * Math.pow(df, 2) +
            b[5] * Math.pow(df, 1) +
            b[6]
        );
    },
    addStdev = function (endpoint) {
        const {data_type, variance_type, groups} = endpoint.data;
        if (data_type !== "C") {
            return;
        }
        switch (variance_type) {
            case 1:
                groups.forEach(d => {
                    d.stdev = _.isFinite(d.variance) ? d.variance : undefined;
                });
                break;
            case 2:
                groups.forEach(d => {
                    d.stdev =
                        _.every([d.n, d.variance], _.isFinite) && d.n > 0
                            ? d.variance * Math.sqrt(d.n)
                            : undefined;
                });
                break;
            default:
                groups.forEach(d => {
                    d.stdev = undefined;
                });
                break;
        }
    },
    addContinuousConfidenceIntervals = function (endpoint) {
        /*
        Approximation; only used during forms; after save calculated more robustly on server
        */
        endpoint.data.groups.forEach(d => {
            let lower_ci, upper_ci;
            if (_.every([d.n, d.stdev, d.response], _.isFinite) && d.n > 0) {
                var se = d.stdev / Math.sqrt(d.n),
                    z = inv_tdist_05(d.n - 1) || 1.96;
                lower_ci = d.response - se * z;
                upper_ci = d.response + se * z;
            }
            d.lower_ci = lower_ci;
            d.upper_ci = upper_ci;
        });
    },
    addDichotomousConfidenceIntervals = function (endpoint) {
        /*
        Procedure adds confidence intervals to dichotomous datasets.
        Add confidence intervals to dichotomous datasets. (pg 80)
        https://www.epa.gov/sites/production/files/2020-09/documents/bmds_3.2_user_guide.pdf
        */
        endpoint.data.groups.forEach(d => {
            let lower_ci, upper_ci;
            if (_.every([d.n, d.incidence], _.isFinite) && d.n > 0 && d.n >= d.incidence) {
                let p = d.incidence / d.n,
                    q = 1 - p,
                    z = 1.959963984540054,
                    z2 = z * z,
                    tmp1 = 2 * d.n * p + z2,
                    tmp2 = 2 + 1 / d.n,
                    tmp3 = 2 * (d.n + z2);
                lower_ci = (tmp1 - 1 - z * Math.sqrt(z2 - tmp2 + 4 * p * (d.n * q + 1))) / tmp3;
                upper_ci = (tmp1 + 1 + z * Math.sqrt(z2 + tmp2 + 4 * p * (d.n * q - 1))) / tmp3;
            }
            d.lower_ci = lower_ci;
            d.upper_ci = upper_ci;
        });
    };
export {
    addContinuousConfidenceIntervals,
    addDichotomousConfidenceIntervals,
    addStdev,
    gammaCDF,
    inv_tdist_05,
    normalCDF,
};
