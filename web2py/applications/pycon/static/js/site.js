/* Author: 

*/

$(function() {
  var search_text = 'Search this site';
  $("#search input[type=search]").click(function() {
    if ($(this).val() === search_text) {
      $(this).val('');
    }
  }).change(function() {
    if ($(this).val() === '') {
      $(this).val(search_text);
    }
  });
  $(".tohide").hide();
  if (!$.browser.msie) {
    $("select.list").multiselect({
      sortable: false, 
      searchable: false,
      nodeComparator: function(node1,node2) {
        var text1 = node1.text(),
            text2 = node2.text();
        return text1 == text2 ? 0 : (text1 < text2 ? -1 : 1);
      }
    });
    $(".ui-multiselect").width("400px").height("233px").css("border", "0").css("margin", "0");
    $(".ui-multiselect").find("div.selected, div.available").width("185px");
    $(".ui-multiselect").find("ul.selected, ul.available").height("200px");
    $(".ui-multiselect").parent(".w2p_fw").width("400px").height("260px");
  }
  $(".growl").each(function () {
    $.jGrowl($(this).html());
  });

  $('#slider').nivoSlider({
    effect: 'fade', //Specify sets like: 'fold,fade,sliceDown'
    slices: 15,
    animSpeed: 500, //Slide transition speed
    pauseTime: 3000,
    startSlide: 0, //Set starting Slide (0 index)
    directionNav: true, //Next & Prev
    directionNavHide: true, //Only show on hover
    controlNav: false, //1,2,3...
    controlNavThumbs: false, //Use thumbnails for Control Nav
    controlNavThumbsFromRel: false, //Use image rel for thumbs
    controlNavThumbsSearch: '.jpg', //Replace this with...
    controlNavThumbsReplace: '_thumb.jpg', //...this in thumb Image src
    keyboardNav: false, //Use left & right arrows
    pauseOnHover: true, //Stop animation while hovering
    manualAdvance: false, //Force manual transitions
    captionOpacity: 0.8, //Universal caption opacity
    beforeChange: function(){},
    afterChange: function(){},
    slideshowEnd: function(){}, //Triggers after all slides have been shown
    lastSlide: function(){}, //Triggers when last slide is shown
    afterLoad: function(){} //Triggers when slider has loaded
  });
  $("#sliderbox").show();
});
