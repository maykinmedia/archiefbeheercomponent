const webpack = require('webpack');
var paths = require('./build/paths');
var argv = require('yargs').argv;
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

var isProduction = process.env.NODE_ENV === 'production';
if (argv.production) {
    isProduction = true;
}

/**
 * Webpack configuration
 * Run using "webpack" or "npm run build"
 */
module.exports = {
    // Path to the js entry point (source).
    entry: {
        [`${paths.package.name}-css`]: `${__dirname}/${paths.scssEntry}`,
        [`admin_overrides`]:  `${__dirname}/${paths.sourcesRoot}sass/admin/admin_overrides.scss`,
        [`core-css`]:  `${__dirname}/${paths.sourcesRoot}sass/screen.scss`,
        [`core-js`]:  `${__dirname}/${paths.sourcesRoot}js/index.js`,
    },

    // Path to the (transpiled) js
    output: {
        path: __dirname + '/' + paths.jsDir, // directory
        filename: '[name].js' // file
    },

    plugins: [
        new MiniCssExtractPlugin(),
        new webpack.DefinePlugin({
            STATIC_URL: JSON.stringify(process.env.STATIC_URL ?? '/static/'),
        }),
        new webpack.ProvidePlugin({
            _: 'lodash',
        }),
    ],

    // Use --production to optimize output.
    mode: isProduction ? 'production' : 'development',

    // Add babel (see .babelrc for settings)
    module: {
        rules: [
            {
                exclude: /node_modules/,
                loader: 'babel-loader',
                test: /.js?$/
            },
            // .scss
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    // Writes css files.
                    MiniCssExtractPlugin.loader,

                    // Loads CSS files.
                    {
                        loader: 'css-loader',
                        options: {
                            url: false
                        },
                    },

                    // Runs postcss configuration (postcss.config.js).
                    {
                        loader: 'postcss-loader'
                    },

                    // Compiles .scss to .css.
                    {
                        loader: 'sass-loader',
                        options: {
                            sassOptions: {
                                comments: false,
                                style: 'compressed'
                            },
                            sourceMap: argv.sourcemap
                        },
                    },
                ],
            }
        ]
    },

    // Use --sourcemap to generate sourcemap.
    devtool: argv.sourcemap ? 'sourcemap' : false,
}
