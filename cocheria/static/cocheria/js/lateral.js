window.onscroll = function() {PegarMenu()};


var menu_boton = document.getElementById("boton-menu");
var sticky_menu = menu_boton.offsetTop;

function PegarMenu() {
  if (window.pageYOffset >= sticky_menu) {
      menu_boton.classList.add("sticky_menu");} 
  else {
      menu_boton.classList.remove("sticky_menu");
  }
}

function openNav() {
  document.getElementById("menuLateral").style.width = "250px";
  document.getElementById("contenedor").style.marginLeft = "250px";
  document.getElementsById("pie").style.marginLeft = "250px";
}

function closeNav() {
  document.getElementById("menuLateral").style.width = "0";
  document.getElementById("contenedor").style.marginLeft= "0";
  document.getElementsById("pie").style.marginLeft = "0";
  document.body.style.backgroundColor = "white";
} 
