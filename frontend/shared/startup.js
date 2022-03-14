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
    console.log(getCookie("sessionid"))
    console.log(exp_date)
    // if exp_date within 15 mins of Date.now()
    if (confirm("Your session is about to expire. Click OK to refresh the session")) {
        $.post("/update-session/", { refresh: true })
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
    // setInterval(checkSession, 60000)
});
