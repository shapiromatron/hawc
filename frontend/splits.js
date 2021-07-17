const startup = (name, cb) => {
    // big switch statement for successful webpack splitting and compilation
    switch (name) {
        case "assessmentSizeStartup":
            import("./admin/assessmentSize/index.js").then(app => cb(app.default));
            break;
        case "adminGrowthStartup":
            import("./admin/growth/index.js").then(app => cb(app.default));
            break;
        case "animalStartup":
            import("./animal/index.js").then(app => cb(app.default));
            break;
        case "bmds2Startup":
            import("./bmd/bmds2/index.js").then(app => cb(app.default));
            break;
        case "epiStartup":
            import("./epi/index.js").then(app => cb(app.default));
            break;
        case "epimetaStartup":
            import("./epimeta/index.js").then(app => cb(app.default));
            break;
        case "invitroStartup":
            import("./invitro/index.js").then(app => cb(app.default));
            break;
        case "litStartup":
            import("./lit/index.js").then(app => cb(app.default));
            break;
        case "mgmtStartup":
            import("./mgmt/index.js").then(app => cb(app.default));
            break;
        case "riskofbiasStartup":
            import("./riskofbias/index.js").then(app => cb(app.default));
            break;
        case "studyStartup":
            import("./study/index.js").then(app => cb(app.default));
            break;
        default:
            throw "Unknown startup request";
    }
};

export default startup;
