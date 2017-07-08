/* must load  "//www.googleadservices.com/pagead/conversion_async.js" and facebook pexel code first */

/*
From:
 https://stackoverflow.com/questions/33608917/multiple-goog-report-conversion-tags-on-one-page-google-adwords-conversion-tra */



goog_conversion_wrapper = function(conversion_id, conversion_label, url) {
    /* <![CDATA[ */

var w = window;
w.google_conversion_id = conversion_id;
w.google_conversion_label = conversion_label;
w.google_remarketing_only = false;

goog_report_conversion(url);
}
// DO NOT CHANGE THE CODE BELOW.
goog_report_conversion = function(url) {

window.google_conversion_format = "3";
window.google_is_call = true;
var opt = new Object();
opt.onload_callback = function() {
if (typeof(url) != 'undefined') {
  //window.location = url;
}
}
var conv_handler = window['google_trackConversion'];
if (typeof(conv_handler) == 'function') {
conv_handler(opt);
}
/* ]]> */

}




/*
Scripts to track certain events.
 */


/* Track if someone is scheduling with youcanbook.me
* Add the class 'track-schedule-click' to any html tag.
* */
var track_schedule_click = function (url) {
    goog_conversion_wrapper(855486824, 'EnLsCJK08HIQ6OL2lwM', url); // google tracking

    // facebook tracking
    fbq('track', 'Lead', {
    value: 0.00,
    currency: 'USD'
    });
};

$('.track-schedule-click').click(function(){
    track_schedule_click($(this).attr('href'));
});

