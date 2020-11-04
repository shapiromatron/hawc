const toggleSidebarCollapse = function(isCollapsed, submit) {
        const toggleText = isCollapsed
            ? "<i class='fa fa-2x fa-angle-double-right'/>"
            : "<i class='fa fa-2x fa-angle-double-left' />";
        $("#sidebar-container")
            .data("collapsed", isCollapsed)
            .toggleClass("sidebar-collapsed", isCollapsed);
        $("#toggle-sidebar").html(toggleText);

        if (submit) {
            const url = $("#sidebar-container").data("url");
            $.post(url, {hideSidebar: isCollapsed});
        }
    },
    sidebarStartup = function() {
        if (document.getElementById("sidebar-container") === null) {
            return;
        }
        $("#toggle-sidebar").click(() => {
            toggleSidebarCollapse(!$("#sidebar-container").data("collapsed"), true);
        });
    };

export default sidebarStartup;
