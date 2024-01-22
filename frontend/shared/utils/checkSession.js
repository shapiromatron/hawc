const checkSession = function () {
    // check on an interval if a user's current session is about to expire. If it is, display
    // a popup to stay logged in.
    let checkId;
    const CHECK_INTERVAL_MS = 60000, // 1 minute (1 min * 60 sec/min * 1000 msec/sec)
        SESSION_EXPIRE_WARNING = 900000, // 15 minutes  (15 min * 60 sec/min * 1000 msec/sec)
        setExpireTime = time => {
            $('meta[name="session_expire_time"]').attr("content", time);
        },
        getExpireTime = () => {
            const expTime = $('meta[name="session_expire_time"]').attr("content");
            return Date.parse(expTime);
        },
        check = function () {
            // if session is about to expire, display a popup to request a session refresh
            const expTime = getExpireTime();
            if (expTime - Date.now() < SESSION_EXPIRE_WARNING) {
                const resp = confirm(
                    "Your current session will expire in 15 minutes. Please click OK to stay logged in."
                );
                if (resp) {
                    // confirmed request; cancel this interval check and make request
                    clearInterval(checkId); // prevent popup stacking on top of each other
                    $.post("/update-session/", {refresh: true}).done(response => {
                        // session update failed; go home
                        if (response.new_expiry_time === null) {
                            window.location = "/";
                            return;
                        }
                        setExpireTime(response.new_expiry_time);
                        checkId = setInterval(check, CHECK_INTERVAL_MS);
                    });
                }
            }
        };

    // only setup check if we have a valid session expiration
    if (getExpireTime()) {
        checkId = setInterval(check, CHECK_INTERVAL_MS);
    }
};

export default checkSession;
