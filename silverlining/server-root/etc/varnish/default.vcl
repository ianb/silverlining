backend default {
.host = "127.0.0.1";
.port = "8080";
}

sub vcl_pipe {
    # Note that only the first request to the backend will have
    # X-Forwarded-For set.  If you use X-Forwarded-For and want to
    # have it set for all requests, make sure to have:
    set req.http.connection = "close";
    # here.  It is not set by default as it might break some broken web
    # applications, like IIS with NTLM authentication.
    return (pipe);
}

sub vcl_recv {
    set req.http.X-Varnish-IP = server.ip;
    # Add a unique header containing the client address
    remove req.http.X-Forwarded-For;
    set req.http.X-Forwarded-For = client.ip;
    if (req.request == "POST") {
        return(pass);
    }
    if (req.request != "GET" && req.request != "HEAD" &&
        req.request != "PUT" && req.request != "POST" &&
        req.request != "TRACE" && req.request != "OPTIONS" &&
        req.request != "DELETE") {

        # Non-RFC2616 or CONNECT which is weird. #
        return(pass);
    }
    if (req.http.Authorization) {
        # Not cacheable by default #
        return(pass);
    }
}

sub vcl_fetch {
    if(beresp.http.Pragma ~ "no-cache" ||
       beresp.http.Cache-Control ~ "no-cache" ||
       beresp.http.Cache-Control ~ "private") {
            return(pass);
    }
    if (beresp.status >= 300) {
        return(pass);
    }
    # Django regularly sends pages with Set-Cookie and cache control, 
    # we'll ignore Cache-Control in that case, as there's no point to
    # caching something that sets a cookie.
    if (beresp.http.Set-Cookie) {
        unset beresp.http.Cache-Control;
        return(pass);
    }
    if (beresp.http.Cache-Control ~ "max-age" || beresp.http.Expires) {
        unset beresp.http.Set-Cookie;
        return(deliver);
    }
    # Apache adds Vary: X-Forwarded-For to each response, which would
    # mean a separate cache for each client; not our intent, so we'll
    # ignore it:
    set beresp.http.Vary = regsub(beresp.http.Vary, "X-Forwarded-For,", "");
    return(pass);
}

sub vcl_hit {
    if (!obj.cacheable) {
        return(pass);
    }

    if (req.http.Cache-Control ~ "no-cache") {
        # Ignore requests via proxy caches,  IE users and badly behaved crawlers
        # like msnbot that send no-cache with every request.
        if (! (req.http.Via || req.http.User-Agent ~ "bot|MSIE")) {
            set obj.ttl = 0s;
            return (restart);
        } 
    }
    return(deliver);
}
