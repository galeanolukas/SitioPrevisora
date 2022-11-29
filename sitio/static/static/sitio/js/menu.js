window.onscroll = function() {pegarMenu(), ShowFlechaUp()};
//window.onscroll = function() {ShowFlechaUp()};

var navbar = document.getElementById("Barra");
var subnavbar = document.getElementById("Subbarra");
var sticky = navbar.offsetTop;


var slideIndex = 0;

function pegarMenu() {
  if (window.pageYOffset >= sticky) {
    navbar.classList.add("sticky")
    navbar.classList.add('trans-navbar')
    navbar.style.borderRadius = "0px"
    subnavbar.classList.add("sticky")
  } else {
    navbar.classList.remove("sticky")
    navbar.style.borderRadius = "10px"
    subnavbar.classList.remove("sticky")
  }
}

function MostrarMenu() {
  var x = document.getElementById("Barra");
  if (x.className === "navbar") {
    x.className += " responsive";
  } else {
    x.className = "navbar";
  }
}

function ShowFlechaUp() {
  if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
    document.getElementById("flotante-up").style.display = "block";
  } else {
    document.getElementById("flotante-up").style.display = "none";
  }
}

function VolverAlTop() {
	return o("html, body").stop().animate({
		scrollTop: 0
		}, t.scrollSpeed, t.easingType), !1
}


  
