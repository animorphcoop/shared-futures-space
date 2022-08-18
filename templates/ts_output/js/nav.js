"use strict";
var mainNavLink = document.getElementById('burger');
var nav = document.getElementById('menu');
var subNav = document.getElementById('dropdownNav');
console.log(subNav);
// Toggle menu
function navToggle() {
    mainNavLink.classList.toggle('hidden');
    nav.classList.toggle('hidden');
}
// Toggle Submenu
function subNavToggle() {
    subNav.classList.toggle('hidden');
}
