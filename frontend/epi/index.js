export default cb => import("./split.js").then(app => cb(app.default));
