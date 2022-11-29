var slideIndex = 0;
carousel();

function carousel() {
  var i;
  var x = document.getElementsByClassName("header");
  for (i = 0; i < x.length; i++) {
    x.style.background-image = "url('/static/header/banner2.png')";
  }
  slideIndex++;
  if (slideIndex > x.length) {slideIndex = 1}
  x.style.background-image = "url('/static/header/banner2.png')";
  setTimeout(carousel, 2000); // Change image every 2 seconds
} 
