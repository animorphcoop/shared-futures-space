"use strict";
var mainNavLink = document.getElementById('burger');
var nav = document.getElementById('menu');
var subNav = document.getElementById('dropdownNav');
// Toggle menu
function navToggle() {
    mainNavLink === null || mainNavLink === void 0 ? void 0 : mainNavLink.classList.toggle('hidden');
    nav === null || nav === void 0 ? void 0 : nav.classList.toggle('hidden');
}
// Toggle Submenu
function subNavToggle() {
    subNav === null || subNav === void 0 ? void 0 : subNav.classList.toggle('hidden');
}
