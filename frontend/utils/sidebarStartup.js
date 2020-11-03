const toggleSidebarCollapse = function() {
        $(".menu-collapsed").toggleClass("d-none");
        $(".sidebar-submenu").toggleClass("d-none");
        $(".submenu-icon").toggleClass("d-none");
        $("#sidebar-container").toggleClass("sidebar-expanded sidebar-collapsed");

        // Treating d-flex/d-none on separators with title
        var title = $(".sidebar-separator-title");
        if (title.hasClass("d-flex")) {
            title.removeClass("d-flex");
        } else {
            title.addClass("d-flex");
        }

        // Collapse/Expand icon
        $("#collapse-icon").toggleClass("fa-angle-double-left fa-angle-double-right");
    },
    sidebarStartup = function() {
        if (document.getElementById("sidebar-container") === null) {
            return;
        }

        // Hide submenus
        $("#body-row .collapse").collapse("hide");

        // Collapse/Expand icon
        $("#collapse-icon").addClass("fa-angle-double-left");

        // Collapse click
        $("[data-toggle=sidebar-colapse]").click(toggleSidebarCollapse);
    };

export default sidebarStartup;
