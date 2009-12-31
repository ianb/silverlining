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
}

sub vcl_fetch {
    if (obj.http.cache-control == "no-cache") {
        return (pass);
    }
}
