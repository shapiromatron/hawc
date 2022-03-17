const checkSession = function() {
    const INTERVAL_MS = 60000; // 1 minute
    const SESSION_EXPIRE_WARNING = 900000; // 15 minutes
    var intervalID;

    const check = function() {
        // if session is about to expire, then display a popup to allow a session refresh
        let exp_time = $('meta[name="session_expire_time"]').attr("content");
        exp_time = Date.parse(exp_time);

        if (exp_time - Date.now() < SESSION_EXPIRE_WARNING) {
            clearInterval(intervalID); // prevents multiple popups stacking on top of each other
            if (confirm("Your session will expire in 15 minutes. Click OK to stay logged in.")) {
                $.post("/update-session/", {refresh: true}).done(response => {
                    $('meta[name="session_expire_time"]').attr("content", response.new_expiry_time);
                });
            }
            intervalID = setInterval(check, INTERVAL_MS);
        }
    };

    intervalID = setInterval(check, INTERVAL_MS);
};

export default checkSession;
