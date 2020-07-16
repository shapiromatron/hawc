import * as d3 from "d3";
import $ from "$";
import _ from "lodash";

import Quillify from "./Quillify";

// Extend JS built-ins
Object.defineProperty(Object.prototype, "rename_property", {
    value(old_name, new_name) {
        try {
            this[new_name] = this[old_name];
            delete this[old_name];
        } catch (f) {
            console.warn("prop not found");
        }
    },
});

_.extend(Date.prototype, {
    toString() {
        var pad = function(x) {
            return (x < 10 ? "0" : "") + x;
        };
        if (this.getTime()) {
            var d = pad(this.getDate());
            var m = pad(this.getMonth() + 1);
            var y = this.getFullYear();
            var hr = pad(this.getHours());
            var min = pad(this.getMinutes());
            return [y, m, d].join("/") + " " + hr + ":" + min;
        }
        return null;
    },
});

_.extend(String, {
    hex_to_rgb(hex) {
        // http://stackoverflow.com/questions/5623838/
        hex = hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, function(m, r, g, b) {
            return r + r + g + g + b + b;
        });

        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
            ? {
                  r: parseInt(result[1], 16),
                  g: parseInt(result[2], 16),
                  b: parseInt(result[3], 16),
              }
            : null;
    },
    contrasting_color(hex) {
        // http://stackoverflow.com/questions/1855884/
        var rgb = String.hex_to_rgb(hex),
            a = 1 - (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
        return a < 0.5 ? "#404040" : "#ffffff";
    },
});

_.extend(Array.prototype, {
    splice_object(obj) {
        if (this.length === 0) return this;
        for (var i = this.length - 1; i >= 0; i -= 1) {
            if (this[i] === obj) {
                this.splice(i, 1);
            }
        }
    },
});

_.extend(Math, {
    GammaCDF(x, a) {
        // adapted from http://www.math.ucla.edu/~tom/distributions/gamma.html
        var gcf = function(X, A) {
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
            gser = function(X, A) {
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
            logGamma = function(Z) {
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
            GI;

        if (x <= 0) {
            GI = 0;
        } else if (a > 200) {
            var z = (x - a) / Math.sqrt(a);
            var y = Math.normalcdf(z);
            var b1 = 2 / Math.sqrt(a);
            var phiz = 0.39894228 * Math.exp((-z * z) / 2);
            var w = y - (b1 * (z * z - 1) * phiz) / 6; //Edgeworth1
            var b2 = 6 / a;
            var u = 3 * b2 * (z * z - 3) + b1 * b1 * (z ^ (4 - 10 * z * z + 15));
            GI = w - (phiz * z * u) / 72; //Edgeworth2
        } else if (x < a + 1) {
            GI = gser(x, a);
        } else {
            GI = gcf(x, a);
        }
        return GI;
    },
    normalcdf(X) {
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
    inv_tdist_05(df) {
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
                7.9703237683e-5,
                -3.5145890027e-3,
                0.063259191874,
                -0.5963723075,
                3.129413441,
                -8.8538894383,
                13.358101926,
            ];
        } else if (df < 62) {
            b = [
                1.1184055716e-10,
                -2.7885328039e-8,
                2.8618499662e-6,
                -1.5585120701e-4,
                4.8300645273e-3,
                -0.084316656676,
                2.7109288893,
            ];
        } else {
            b = [
                5.1474329765e-16,
                -7.262226388e-13,
                4.2142967681e-10,
                -1.2973354626e-7,
                2.275308052e-5,
                -2.2594979441e-3,
                2.0766977669,
            ];
            if (df > 350) {
                console.warn("Extrapolating beyond inv_tdist_05 regression range (N>350).");
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
    log10(val) {
        // required for IE
        return Math.log(val) / Math.LN10;
    },
    mean(array) {
        switch (array.length) {
            case 0:
                return null;
            case 1:
                return array[0];
            default:
                var sum = 0,
                    err = false;
                array.forEach(function(v) {
                    if (typeof v !== "number") {
                        err = true;
                    }
                    sum += v;
                });
        }
        if (err === false && isFinite(sum)) {
            return sum / array.length;
        } else {
            return null;
        }
    },
});

_.extend(Number.prototype, {
    toHawcString() {
        if (this === 0) {
            return this.toString();
        } else if (Math.abs(this) > 0.001 && Math.abs(this) < 1e9) {
            // local print "0" for anything smaller than this
            return this.toLocaleString();
        } else {
            // too many 0; use exponential notation
            return this.toExponential(2);
        }
    },
});

$.fn.quillify = Quillify;

// Django AJAX with CSRF protection.
var getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    csrftoken = getCookie("csrftoken"),
    sessionid = getCookie("sessionid"),
    csrfSafeMethod = function(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    };

$.ajaxSetup({
    crossDomain: false,
    beforeSend(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.setRequestHeader("sessionid", sessionid);
        }
    },
});

d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
        this.parentNode.appendChild(this);
    });
};
