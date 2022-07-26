// xs breakpoint: https://getbootstrap.com/docs/4.6/layout/overview/#containers
const XS_BREAKPOINT = 576,
    toggleSidebarCollapse = function(isCollapsed, submit) {
        const toggleText = isCollapsed
            ? "<i class='fa fa-2x fa-angle-double-right'/>"
            : "<i class='fa fa-2x fa-angle-double-left' />";
        $("#sidebar-container")
            .data("collapsed", isCollapsed)
            .toggleClass("sidebar-collapsed", isCollapsed);
        $("#toggle-sidebar").html(toggleText);
        $(".sidebar-link-holder").toggleClass("hidden");

        if (submit) {
            const url = $("#sidebar-container").data("url");
            $.post(url, {hideSidebar: isCollapsed});
        }
    },
    sidebarStartup = function() {
        if (document.getElementById("sidebar-container") === null) {
            return;
        }
        if ($("#sidebar-container").data("collapsed") == "unset") {
            if ($(document).width() < XS_BREAKPOINT) {
                toggleSidebarCollapse(true, true);
            }
        }
        $("#toggle-sidebar").click(e => {
            const isCollapsed = $("#sidebar-container").hasClass("sidebar-collapsed");
            e.preventDefault();
            toggleSidebarCollapse(!isCollapsed, true);
        });
    };

export default sidebarStartup;
