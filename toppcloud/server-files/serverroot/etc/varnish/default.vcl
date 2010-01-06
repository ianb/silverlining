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
        pass;
    }
    if (req.request != "GET" && req.request != "HEAD" &&
        req.request != "PUT" && req.request != "POST" &&
        req.request != "TRACE" && req.request != "OPTIONS" &&
        req.request != "DELETE") {

        # Non-RFC2616 or CONNECT which is weird. #
        pass;
    }
    if (req.http.Authorization) {
        # Not cacheable by default #
        pass;
    }
}

sub vcl_fetch {
    if(obj.http.Pragma ~ "no-cache" ||
       obj.http.Cache-Control ~ "no-cache" ||
       obj.http.Cache-Control ~ "private") {
            pass;
    }
    if (obj.status >= 300) {
        pass;
    }
    if (obj.http.Cache-Control ~ "max-age" || obj.http.Expires) {
        unset obj.http.Set-Cookie;
        deliver;
    }
    pass;
}

sub vcl_hit {
    if (!obj.cacheable) {
        pass;
    }

    if (req.http.Cache-Control ~ "no-cache") {
        # Ignore requests via proxy caches,  IE users and badly behaved crawlers
        # like msnbot that send no-cache with every request.
        if (! (req.http.Via || req.http.User-Agent ~ "bot|MSIE")) {
            set obj.ttl = 0s;
            return (restart);
        } 
    }
    deliver;
}
