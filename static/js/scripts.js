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

// Search suggestions functionality
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const suggestionsList = document.getElementById("suggestions");

    if (searchInput && suggestionsList) {
        searchInput.addEventListener("input", function () {
            const query = this.value.trim();

            if (query.length < 2) {
                suggestionsList.innerHTML = '';
                return;
            }

            fetch(`/suggest?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsList.innerHTML = '';
                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        li.style.padding = '8px';
                        li.style.cursor = 'pointer';
                        li.addEventListener('click', function () {
                            searchInput.value = item;
                            suggestionsList.innerHTML = '';
                            searchInput.form.submit(); // submit
                        });
                        suggestionsList.appendChild(li);
                    });
                });
        });
    }
});
