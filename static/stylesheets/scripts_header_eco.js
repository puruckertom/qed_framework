$(document).ready(function() {
  // Remove Log-in
  $('#topheader_p p, .logreg').hide();
  // Index link
  $('.index_link').click(function(e) {
    e.preventDefault();
    var destination = $(this).attr('href');
    setTimeout(function() { window.location.href = destination; }, 500);
    $('#topheader_pic, #topheader_p').animate({
      height:'240px'
    }, 500);
    $('.logreg').fadeIn(500);
  });
  // BlockUI on QAQC
  $("a[class^='fadeQAQC']").click(function (e) {
    e.preventDefault();
    cur_url = window.location.href;
    if (cur_url.indexOf('qaqc') == -1) {
      $.blockUI({
        css:{ "top":""+wintop+"", "left":""+winleft+"", "padding": "30px 20px", "width": "400px", "height": "60px", "border": "0 none", "border-radius": "4px", "-webkit-border-radius": "4px", "-moz-border-radius": "4px", "box-shadow": "3px 3px 15px #333", "-webkit-box-shadow": "3px 3px 15px #333", "-moz-box-shadow": "3px 3px 15px #333" },
        message: '<h2 class="popup_header">Processing QA/QC...</h2><br/><img src="/static/images/loader.gif" style="margin-top:-16px">',
        fadeIn:  500
      });
      if (cur_url.indexOf(model+'/') !== -1) {
        setTimeout(function() {window.location.href = "qaqc";}, 500);
      } else {
        setTimeout(function() {window.location.href = model+"/qaqc";}, 500);
      }
    }
  });

});