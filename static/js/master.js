$('.btn-toggle').on('click', function (e) {
  var $this = $(this);
  if ($this.hasClass('btn-danger')) {
    $this.removeClass('btn-danger');
    $this.addClass('btn-success');
  } else {
    $this.removeClass('btn-success');
    $this.addClass('btn-danger');
  }
  e.preventDefault();
});

$('.navbar-nav li a').click(function(){
  $('.navbar-nav li a').removeClass('active');
  $(this).addClass('active');
})


$(document).ready(function () {
  $(document).on("scroll", onScroll);
  
  //smoothscroll
  $('.navbar-nav li a').on('click', function (e) {
      e.preventDefault();
      $(document).off("scroll");
      
      $('.navbar-nav li a').each(function () {
          $(this).removeClass('active');
      })
      $(this).addClass('active');
    
      var target = this.hash,
          menu = target;
      $target = $(target);
      $('html, body').stop().animate({
          'scrollTop': $target.offset().top-2
      }, 500, 'swing', function () {
          window.location.hash = target;
          $(document).on("scroll", onScroll);
      });
  });
});

function onScroll(event){
  var scrollPos = $(document).scrollTop();
  $('.navbar-nav li a').each(function () {
      var currLink = $(this);
      var refElement = $(currLink.attr("href"));
      if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
          $('.navbar-nav li a').removeClass("active");
          currLink.addClass("active");
      }
      else{
          currLink.removeClass("active");
      }
  });
}