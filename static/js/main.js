document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link:not(.dropdown-toggle)');
    navLinks.forEach(function (link) {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });
});
