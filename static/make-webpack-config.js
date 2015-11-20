var path = require("path");
var webpack = require('webpack');
var autoprefixer = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var CompressionPlugin = require("compression-webpack-plugin");
var mkdirp = require('mkdirp');


module.exports = function (options) {
    var entry = {
        main: ["webpack/hot/dev-server", "./assets/entry"]
    };
    var output = {
        path: path.resolve('build/public'),
        filename: options.longTermCaching ? "[name]-[hash].js" : "[name].js"
    };
    var plugins = [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }),
        new ExtractTextPlugin(options.longTermCaching ? '[name]-[hash].css' : '[name].css'),
        new CompressionPlugin({
            asset: "{file}.gz",
            algorithm: "gzip",
            regExp: /\.js$|\.html|\.css$/,
            //threshold: 10240,
            //minRatio: 0.8
        }),
        new BundleTracker({filename: path.relative(__dirname, path.join(output.path, 'webpack-stats.json'))}),
    ];
    var loaders = [
        {test: /\.jsx?$/, exclude: /(node_modules|bower_components)/, loader: 'babel-loader'},
        {test: /\.css$/, loader: ExtractTextPlugin.extract('style-loader', 'css-loader!postcss-loader')},
        {test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, loader: "file"},
        {test: /\.(woff|woff2)$/, loader: "url?prefix=font/&limit=5000"},
        {test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, loader: "url?limit=10000&mimetype=application/octet-stream"},
        {test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, loader: "url?limit=10000&mimetype=image/svg+xml"}
    ];
    mkdirp.sync(output.path)

    return {
        entry: entry,
        output: output,
        plugins: plugins,
        devtool: options.devtool,
        debug: options.debug,
        module: {
            loaders: loaders,
        },
        postcss: [
            autoprefixer({
                browsers: ['last 2 versions']
            })
        ],
        resolve: {
            modulesDirectories: ['node_modules'],
            extensions: ['', '.js', '.jsx', '.css']
        },
    };
};
