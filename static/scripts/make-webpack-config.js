/*jslint node: true */
var path = require("path");
var webpack = require('webpack');
var autoprefixer = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var CompressionPlugin = require("compression-webpack-plugin");
var Clean = require('clean-webpack-plugin');
var mkdirp = require('mkdirp');


module.exports = function (options) {
    var baseDir = path.dirname(__dirname);
    var entry = {
        main: options.hotComponents ? ["webpack/hot/dev-server", "./assets/entry"] : "./assets/entry"
    };
    var publicPath = options.devServer ? "http://localhost:2992/static/assets/" :
        "/static/assets/";
    var buildRoot = path.resolve('./build');
    var output = {
        path: path.join(buildRoot, 'assets'),
        publicPath: publicPath,
        filename: options.longTermCaching ? "[name]-[hash].js" : "[name].js",
        pathinfo: options.debug
    };
    var plugins = [
        // cleanup build path
        new Clean([buildRoot + '/**/*.*']),
        // provide jQuery for bootstrap
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }),
        /* prod */
        options.minimize && new webpack.DefinePlugin({
            'process.env': {
                // This has effect on the react lib size
                'NODE_ENV': JSON.stringify('production')
            }
        }),
        options.minimize && new webpack.optimize.DedupePlugin(),
        options.minimize && new webpack.optimize.UglifyJsPlugin({
            compressor: {
                warnings: false
            }
        }),
        options.minimize && new webpack.NoErrorsPlugin(),
        options.separateStylesheet && new ExtractTextPlugin(
            options.longTermCaching ? '[name]-[hash].css' : '[name].css'
        ),
        options.minimize && new CompressionPlugin({
            asset: "{file}.gz",
            algorithm: "gzip",
            regExp: /\.js$|\.html|\.css$/,
            //threshold: 10240,
            //minRatio: 0.8
        }),
        // generate webpack-stats.json for django-webpack-loader integration
        new BundleTracker({filename: path.relative(baseDir, path.join(options.debug ? baseDir : buildRoot, 'webpack-stats.json'))}),
    ].filter(Boolean); // remove empty rules

    var loaders = [
        // ES6 support with babel2 (look into .babelrc for list of features)
        {test: /\.jsx?$/, exclude: /(node_modules|bower_components)/, loader: 'babel-loader'},
        {
            test: /\.css$/,
            loader: options.separateStylesheet ? ExtractTextPlugin.extract('style-loader', 'css-loader!postcss-loader')
                : 'style-loader!css-loader!postcss-loader'
        },
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
