
////////////////////////////////
		//Setup//
////////////////////////////////

// Plugins
var gulp = require('gulp'),
      pjson = require('./package.json'),
      gutil = require('gulp-util'),
      sass = require('gulp-sass'),
      autoprefixer = require('gulp-autoprefixer'),
      cssnano = require('gulp-cssnano'),
      rename = require('gulp-rename'),
      del = require('del'),
      plumber = require('gulp-plumber'),
      pixrem = require('gulp-pixrem'),
      uglify = require('gulp-uglify'),
      imagemin = require('gulp-imagemin'),
      exec = require('child_process').exec,
      runSequence = require('run-sequence'),
      browserSync = require('browser-sync').create(),
      reload = browserSync.reload,
      sourcemaps = require('gulp-sourcemaps');


// Relative paths function
var pathsConfig = function (appName) {
  this.app = "./" + (appName || pjson.name);
  this.appignore ="!./" + (appName || pjson.name);

  return {
    app: this.app,
    templates: this.app + '/templates',
    css: this.app + '/static/css',
    sass: this.app + '/static/sass',
    fonts: this.app + '/static/fonts',
    images: this.app + '/static/images',
    js: this.app + '/static/js',
    ignorejs: this.appignore+'/static/js'
  }
};

var paths = pathsConfig();

////////////////////////////////
		//Tasks//
////////////////////////////////

// Styles autoprefixing and minification
gulp.task('styles', function() {
  return gulp.src(paths.sass + '/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(plumber()) // Checks for errors
    .pipe(autoprefixer({browsers: ['last 2 version']})) // Adds vendor prefixes
    .pipe(pixrem())  // add fallbacks for rem units
    .pipe(gulp.dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cssnano()) // Minifies the result
    .pipe(gulp.dest(paths.css));
});


// Javascript minification
gulp.task('scripts', function() {
  return gulp.src([paths.js + '/**/*.js',paths.ignorejs+'/**/*.min.js'])
      .pipe(plumber()) // Checks for errors
      .pipe(uglify()) // Minifies the js
      .pipe(rename({ suffix: '.min' }))
      .pipe(gulp.dest(paths.js));
});

// Image compression
gulp.task('imgCompression', function(){
  return gulp.src(paths.images + '/*')
    .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
    .pipe(gulp.dest(paths.images))
});

// Run django server
gulp.task('runServer', function() {
  exec('run django python manage.py runserver', function (err, stdout, stderr) {
    console.log(stdout);
    console.log(stderr);
  });
});

// Browser sync server for live reload
gulp.task('browserSync', function() {
    browserSync.init(
      [paths.css + "/*.css", paths.js + "*.js", paths.templates + '/**/*.html'], {
        proxy:  "django:8000"
    });
});

// Default task
gulp.task('default', function() {
    runSequence(['styles', 'scripts', 'imgCompression'], 'browserSync');
});

////////////////////////////////
		//Watch//
////////////////////////////////

// Watch
gulp.task('watch', ['default'], function() {
  gulp.watch(paths.sass + '/**/*.scss', ['styles']);
  gulp.watch(paths.css + '/**/*.css').on("change", reload);
  gulp.watch(paths.js + '/**/*.js', ['scripts']).on("change", reload);
  gulp.watch(paths.images + '/*', ['imgCompression']);
  gulp.watch(paths.templates + '/**/*.html').on("change", reload);

});
