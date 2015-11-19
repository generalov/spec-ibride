module.exports = require('./make-webpack-config')({
    longTermCaching: false,
    debug: true,
    separateStylesheet: false,
    devtool: "eval"
});