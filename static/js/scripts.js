let subMenu = document.getElementById("subMenu");
let blurOverlay = document.getElementById("blurOverlay");
let userImg = document.querySelector(".user");

function toggleMenu() {
    subMenu.classList.toggle("open_menu");
    blurOverlay.classList.toggle("active");
}

// Close menu when clicking the overlay
blurOverlay.addEventListener("click", function() {
    subMenu.classList.remove("open_menu");
    blurOverlay.classList.remove("active");
});

// Close menu when clicking anywhere outside the menu and user image
document.addEventListener("mousedown", function(event) {
    if (
        subMenu.classList.contains("open_menu") &&
        !subMenu.contains(event.target) &&
        !userImg.contains(event.target)
    ) {
        subMenu.classList.remove("open_menu");
        blurOverlay.classList.remove("active");
    }
});

