const menuBtn = document.getElementById("menuToggle");
const sidebar = document.querySelector(".sidebar");

if (menuBtn && sidebar) {

    menuBtn.addEventListener("click", function () {

        sidebar.classList.toggle("show-sidebar");

    });

}