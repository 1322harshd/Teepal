let subMenu = document.getElementById("subMenu");
let blurOverlay = document.getElementById("blurOverlay");

function toggleMenu() {
    subMenu.classList.toggle("open_menu");
    blurOverlay.classList.toggle("active");
}

// Close menu when clicking outside
blurOverlay.addEventListener("click", function() {
    subMenu.classList.remove("open_menu");
    blurOverlay.classList.remove("active");
});

