import "react-tabs/style/react-tabs.css";

import * as d3 from "d3";

import $ from "$";

import checkSession from "./utils/checkSession";
import Quillify from "./utils/Quillify";
import tryWebAppStartup from "./utils/tryWebAppStartup";

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
    },
    debugStartup = function () {
        if (window.localStorage.getItem("hawc-debug-badge") == "true") {
            $(".debug-badge")
                .on("click", e => {
                    navigator.clipboard.writeText(e.target.closest(".debug-badge").innerText);
                    e.stopPropagation();
                })
                .removeClass("hidden");
        }
    };

$(document).ready(() => {
    setupAjax(document);
    tryWebAppStartup();
    checkSession();
    debugStartup();
});
