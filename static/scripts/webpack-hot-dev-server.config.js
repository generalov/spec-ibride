module.exports = require('./make-webpack-config')({
    longTermCaching: false,
    debug: true,
    hotComponents: true,
    devServer: true,
    separateStylesheet: false,
    minimize: false,
    devtool: "eval"
});
