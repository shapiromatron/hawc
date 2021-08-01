import * as d3 from "d3";
import $ from "$";

import "react-tabs/style/react-tabs.css";

import sidebarStartup from "./utils/sidebarStartup";
import Quillify from "./utils/Quillify";

$.fn.quillify = Quillify;

// Django AJAX with CSRF protection.
const getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    csrftoken = getCookie("csrftoken"),
    sessionid = getCookie("sessionid"),
    csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);

$.ajaxSetup({
    crossDomain: false,
    beforeSend(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.setRequestHeader("sessionid", sessionid);
        }
    },
});

d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
        this.parentNode.appendChild(this);
    });
};

// sidebar startup
sidebarStartup();
