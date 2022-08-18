const mainNavLink = document.getElementById('burger');
const nav = document.getElementById('menu');

const subNav = document.getElementById('dropdownNav');
console.log(subNav)
// Toggle menu
function navToggle() {

  mainNavLink.classList.toggle('hidden');
  nav.classList.toggle('hidden');
}

// Toggle Submenu
function subNavToggle() {

  subNav.classList.toggle('hidden');
}
