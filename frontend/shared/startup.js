import * as d3 from "d3";
import $ from "$";

import "react-tabs/style/react-tabs.css";

import sidebarStartup from "./utils/sidebarStartup";
import tryWebAppStartup from "./utils/tryWebAppStartup";
import Quillify from "./utils/Quillify";
import _ from "lodash";

$.fn.quillify = Quillify;

// Django AJAX with CSRF protection.
const getCookie = function (name) {
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

const checkSession = function () {
    // if session is about to expire, then display a popup to allow a session refresh
    const SESSION_EXPIRE_WARNING = 900000  // 15 minutes
    let exp_time = $('meta[name="session_expire_time"]').attr('content')
    exp_time = Date.parse(exp_time)

    if (exp_time - Date.now() < SESSION_EXPIRE_WARNING) {
        if (confirm("Your session will expire in 15 minutes. Click OK to stay logged in.")) {
            $.post("/update-session/", { refresh: true })
        }
    }

}

d3.selection.prototype.moveToFront = function () {
    return this.each(function () {
        this.parentNode.appendChild(this);
    });
};

const setupAjax = document => {
    // htmx
    document.body.addEventListener("htmx:configRequest", event => {
        event.detail.headers["X-CSRFToken"] = csrftoken;
    });
    // jquery
    $.ajaxSetup({
        crossDomain: false,
        beforeSend(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.setRequestHeader("sessionid", sessionid);
            }
        },
    });
};

$(document).ready(() => {
    sidebarStartup();
    tryWebAppStartup();
    setupAjax(document);
    setInterval(checkSession, 10000)
});
