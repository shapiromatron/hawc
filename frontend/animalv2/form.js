import $ from "$";

const experimentFormStartup = function(form) {
    $(form)
        .find("#id_name")
        .focus();
};

export default document => {
    document.body.addEventListener("htmx:load", e => {
        if (e.target.querySelector(".form-experiment")) {
            experimentFormStartup(e.target);
        }
    });
};
