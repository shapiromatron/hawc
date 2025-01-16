const startup = (name, cb) => {
    // big switch statement for successful webpack splitting and compilation
    switch (name) {
        case "assessmentStartup":
            import("./assessment/index.js").then(app => cb(app.default));
            break;
        case "animalStartup":
            import("./animal/index.js").then(app => cb(app.default));
            break;
        case "animalv2Startup":
            import("./animalv2/index.js").then(app => cb(app.default));
            break;
        case "bmds2Startup":
            import("./bmd/bmds2/index.js").then(app => cb(app.default));
            break;
        case "bmds3Startup":
            import("./bmd/bmds3/index.js").then(app => cb(app.default));
            break;
        case "dataPivotStartup":
            import("./summary/dataPivot/index.js").then(app => cb(app.default));
            break;
        case "epiStartup":
            import("./epi/index.js").then(app => cb(app.default));
            break;
        case "epiv2Startup":
            import("./epiv2/index.js").then(app => cb(app.default));
            break;
        case "epiMetaStartup":
            import("./epimeta/index.js").then(app => cb(app.default));
            break;
        case "heatmapTemplateStartup":
            import("./summary/heatmapTemplate/index.js").then(app => cb(app.default));
            break;
        case "invitroStartup":
            import("./invitro/index.js").then(app => cb(app.default));
            break;
        case "litStartup":
            import("./lit/index.js").then(app => cb(app.default));
            break;
        case "nestedTagEditorStartup":
            import("./shared/nestedTagEditor/index.js").then(app => cb(app.default));
            break;
        case "riskofbiasStartup":
            import("./riskofbias/index.js").then(app => cb(app.default));
            break;
        case "smartTagsStartup":
            import("./shared/smartTags/index.js").then(app => cb(app.default));
            break;
        case "studyStartup":
            import("./study/index.js").then(app => cb(app.default));
            break;
        case "summaryFormsStartup":
            import("./summary/summaryForms/index.js").then(app => cb(app.default));
            break;
        case "summaryStartup":
            import("./summary/summary/index.js").then(app => cb(app.default));
            break;
        case "summaryTableEditStartup":
            import("./summary/summaryTable/editing/index.js").then(app => cb(app.default));
            break;
        case "summaryTableViewStartup":
            import("./summary/summaryTable/viewing/index.js").then(app => cb(app.default));
            break;
        case "summaryInteractivityStartup":
            import("./summary/interactivity/index.js").then(app => cb(app.default));
            break;
        case "textCleanupStartup":
            import("./shared/textCleanup/index.js").then(app => cb(app.default));
            break;
        default:
            throw `Unknown startup request: ${name}`;
    }
};

export default startup;
