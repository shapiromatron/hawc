const BmrHeaderMap = {
    Extra: "%",
    Added: "% AR",
    "Abs. Dev.": "AD",
    "Std. Dev.": "SD",
    "Rel. Dev.": "% RD",
    Point: "Pt",
};

export const formulas = {
        Polynomial:
            "{beta_0} + ({beta_1}*x) + ({beta_2}*Math.pow(x,2)) + ({beta_3}*Math.pow(x,3)) + ({beta_4}*Math.pow(x,4)) + ({beta_5}*Math.pow(x,5)) + ({beta_6}*Math.pow(x,6)) + ({beta_7}*Math.pow(x,7)) + ({beta_8}*Math.pow(x,8))",
        Linear: "{beta_0} + ({beta_1}*x)",
        "Exponential-M2": "{a} * Math.exp({isIncreasing}*{b}*x)",
        "Exponential-M3": "{a} * Math.exp({isIncreasing}*Math.pow({b}*x,{d}))",
        "Exponential-M4": "{a} * ({c}-({c}-1) * Math.exp(-1.*{b}*x))",
        "Exponential-M5": "{a} * ({c}-({c}-1) *  Math.exp(-1.*Math.pow({b}*x,{d})))",
        Power: "{control} + {slope} * Math.pow(x,{power})",
        Hill: "{intercept} + ({v}*Math.pow(x,{n})) / (Math.pow({k},{n}) + Math.pow(x,{n}))",
        Multistage:
            "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))",
        "Multistage-Cancer":
            "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))",
        Weibull:
            "{Background} + (1-{Background}) * (1 - Math.exp( -1.*{Slope} * Math.pow(x,{Power}) ))",
        LogProbit:
            "{background} + (1-{background}) * Math.normalcdf({intercept} + {slope}*Math.log(x))",
        Probit: "Math.normalcdf({intercept} + {slope}*x)",
        Gamma: "{Background} + (1 - {Background}) * Math.GammaCDF(x*{Slope},{Power})",
        LogLogistic:
            "{background} + (1-{background})/( 1 + Math.exp(-1.*{intercept}-1.*{slope}*Math.log(x) ) )",
        Logistic: "1/( 1 + Math.exp(-1*{intercept}-{slope}*x ))",
        "Dichotomous-Hill":
            "{v} * {g} + ({v} - {v} * {g}) / (1 + Math.exp(-1 * {intercept} - {slope} * Math.log(x)))",
    },
    bmdLabelText = function(bmr) {
        let str, val;
        switch (bmr.type) {
            case "Extra":
            case "Added":
            case "Rel. Dev.":
                str = BmrHeaderMap[bmr.type];
                val = bmr.value * 100;
                break;
            case "Abs. Dev.":
            case "Std. Dev.":
            case "Point":
                str = BmrHeaderMap[bmr.type];
                val = bmr.value;
                break;
            default:
                str = bmr.type;
                val = bmr.value;
        }
        return `${val}${str}`;
    },
    CONTINUOUS = "C",
    DICHOTOMOUS = "D",
    DICHOTOMOUS_CANCER = "DC";
