#include "common.h"
#include "request.h"
#include "cache.h"
#include "proxy.h"

#define TEST_NO_CACHE 0

/**
 * constructor
 */
Proxy::Proxy(int port, int cache_capacity) {
    this->request_id = 1;
    this->port = port;
    cache = new Cache(cache_capacity);
}

/**
 * destructor
 */
Proxy::~Proxy() {
    delete cache;
}

/**
 * Initialize proxy socket: socket create, bind and listen
 */
void Proxy::socket_init() {
    this->sockfd = socket(PF_INET, SOCK_STREAM, 0);
    if (this->sockfd == -1) {
        print_error_message("socket() failed");
    }

    struct sockaddr_in proxy_address;
    memset(&proxy_address, 0, sizeof proxy_address);
    proxy_address.sin_family = AF_INET;
    proxy_address.sin_port = htons(this->port);
    proxy_address.sin_addr.s_addr = INADDR_ANY;

    if (bind(this->sockfd, (struct sockaddr *) &proxy_address, sizeof proxy_address) == -1) {
        print_error_message("bind() failed");
    }

    const int backlog = 100;
    if (listen(this->sockfd, backlog) == -1) {
        print_error_message("listen() failed");
    }
}

/**
 * start the proxy
 */
void Proxy::start() {
    while (true) {

        struct sockaddr_in client_address;
        memset(&client_address, 0, sizeof client_address);
        socklen_t client_addr_size = sizeof client_address;
        
        // get client's sockfd, request time, id, and IP address (from_ip)
        int client_sockfd = accept(this->sockfd, (struct sockaddr *) &client_address, &client_addr_size);

        if (client_sockfd == -1) {
            print_error_message("accept() failed");
        }

        std::time_t seconds = std::time(nullptr);
        std::string request_time = std::string(std::asctime(std::gmtime(&seconds)));
        request_time = request_time.substr(0, request_time.find("\n"));

        char client_ip_addr[INET_ADDRSTRLEN];
        if (inet_ntop(AF_INET, &(client_address.sin_addr), client_ip_addr, INET_ADDRSTRLEN) == NULL) {
            print_error_message("inet_ntop() failed");
        }
        std::string client_ip = std::string(client_ip_addr);

        Request* request  = new Request(client_sockfd, client_ip, request_time, this->request_id);
        (this->request_id)++;

        std::thread t(&Proxy::process_request, this, request);
        t.join();
    }
}

void Proxy::process_request(Request *request) {
    Request *req = request;

    // receive original request from the client (contains absolute url)
    std::string original_request;
    const int buf_size = 4096; // enough for HTTP request
    char buf[buf_size]; // buf for request
    int byte_count = recv(req->sockfd, buf, buf_size - 1, 0);
    if (byte_count == -1) {
        perror("recv() failed ");
        return;
    }
    buf[byte_count] = '\0';
    original_request = buf;

    if (byte_count == 0) {
        return;
    }

    // parse the request line
    std::string request_line = original_request.substr(0, original_request.find("\r\n") + 2); // http request line, ex: "GET www.example:8080/index HTTP/1.1 \r\n"

    std::string method = request_line.substr(0, request_line.find(" ")); // method: GET, POST, CONNECT

    std::string tmp = request_line.substr(request_line.find(" ") + 1);
    std::string url = tmp.substr(0, tmp.find(" ")); // absolute url, ex: "http://www.example:8080/index"

    tmp = tmp.substr(tmp.find(" ") + 1);
    std::string protocol = tmp.substr(0, tmp.find("\r\n")); // protocol, ex: "HTTP/1.1"

    // log
    proxy_log << req->id << ": " << original_request.substr(0, original_request.find("\r\n")) << " from " << req->from_ip << " @ " << req->request_time << std::endl;

    // process different HTTP methods
    if (method == "GET") {
        //Check cache for the requested URL
        CacheCell *cache_item = cache->get(url);

        if (cache_item == nullptr) { // cache miss
            // log
            proxy_log << req->id << ": " << "not in cache" << std::endl;

            std::string response = communicate_with_server(original_request, url, method, protocol, req);
            if (response.empty()) {
                delete req;
                return;
            }

            std::string status_code = response.substr(response.find(" ") + 1, 3);

            if (status_code == "200") { // successful response for GET, cache and send repsonse back to the client
                int validation_type = get_validation_type(response, req->id);
                // save cache (NO_CACHE or MUST_REVALIDATE)
                if (validation_type != NO_STORE) {
                    cache_item = create_cache(response, validation_type, req->id); // store validators and validation type in cache
                    cache->put(url, cache_item); // store cache
                }
            } 
            else if (status_code == "304") {
                // log
                proxy_log << req->id << ": NOTE Your browser has cached the website you requested! You may clear your browser's cache." << std::endl;
            }
            else { // response for GET is not "200 OK", do not cache, show error message and close the socket connection
                // log
                std::string msg = response.substr(0, response.find("\r\n"));
                if (status_code[0] == '4') {
                    proxy_log << req->id << ": ERROR " << msg << std::endl;
                }
                else if (status_code[0] == '5') {
                    proxy_log << req->id << ": ERROR " << msg << std::endl;
                }
                else if (status_code[0] == '3') {
                    proxy_log << req->id << ": WARNING " << msg << std::endl;
                }
            }

            std::string response_line = response.substr(0, response.find("\r\n"));

            // log
            proxy_log << req->id << ": Responding " << response_line << std::endl;

            // miss the cache and (1) after finishing caching; (2) no-store; (3) get error reponse
            // in the 3 above cases, all need to send response back to the client
            send_data(response, req->sockfd);

            if (close(req->sockfd) == -1) {
                perror("client socket close() failed");
            }
        }
        else { // cache hit
            // get cache info for revalidation
            std::string if_none_match = "";
            std::string if_modified_since = "";
            std::string revalidation_request = original_request;
            int insert_index = original_request.find("\r\n\r\n") + 2; // index to insert cache revalidation info

            if (!(cache_item->e_tag).empty()) {
                if_none_match = "If-None-Match: " + cache_item->e_tag + "\r\n";
            }

            if (!(cache_item->last_modified).empty()) {
                if_modified_since = "If-Modified-Since: " + cache_item->last_modified + "\r\n";
            }

            // insert cache revalidation info
            revalidation_request.insert(insert_index, if_none_match + if_modified_since);

            // new response may have different cache policy
            if (cache_item->validation_type == NO_CACHE) { // no-cache, must revalidate every time
                // log
                proxy_log << req->id << ": " << "in cache, requires validation" << std::endl;

                // add cache info in request headers, and send it to server to revalidate the cache
                std::string response = communicate_with_server(revalidation_request, url, method, protocol, req);
                if (response.empty()) {
                    delete req;
                    return;
                }
                
                std::string status_code = response.substr(response.find(" ") + 1, 3);
                
                if (status_code == "304") { // cache contents not modified
                    send_data(cache_item->response, req->sockfd);
                    std::string msg = (cache_item->response).substr(0, cache_item->response.find("\r\n"));

                    // log
                    proxy_log << req->id << ": Responding " << msg << std::endl;
                }
                else if (status_code[0] == '2') { // cache contents need to be updated
                    send_data(response, req->sockfd);

                    // log
                    std::string msg = response.substr(0, response.find("\r\n"));
                    proxy_log << req->id << ": Responding " << msg << std::endl;

                    int validation_type = get_validation_type(response, req->id);

                    if (validation_type == NO_STORE) {
                        cache->remove(url);
                    }
                    else { // update cache_item (no-cache or must-revalidate)
                        cache_item = create_cache(response, validation_type, req->id);
                        cache->put(url, cache_item);
                    }
                }
                else { // response indicates error, warning or note when updating cache, get message for updating cache from server
                    // log
                    std::string msg = response.substr(0, response.find("\r\n"));
                    if (status_code[0] == '4') {
                        proxy_log << req->id << ": ERROR " << msg << std::endl;
                    }
                    else if (status_code[0] == '5') {
                        proxy_log << req->id << ": ERROR " << msg << std::endl;
                    }
                    else if (status_code[0] == '3') {
                        proxy_log << req->id << ": WARNING " << msg << std::endl;
                    }
                    proxy_log << req->id << ": Responding " << msg << std::endl; // log
                    send_data(response, req->sockfd);
                }

                if (close(req->sockfd) == -1) {
                    perror("client socket close() failed");
                }
            }
            else if (cache_item->validation_type == MUST_REVALIDATE) { // hit, need revalidation if stale
                // check if expired
                std::time_t cur_seconds = std::time(nullptr);
                if (cache_item->isExpired(cur_seconds)) { // cache expired
                    std::string expired_time;
                    if (cache_item->max_age != -1) {
                        std::time_t expired_seconds = cache_item->cache_time + cache_item->max_age;
                        expired_time = std::string(std::asctime(std::gmtime(&expired_seconds)));
                    }
                    else {
                        expired_time = std::string(std::asctime(std::gmtime(&(cache_item->expires_date))));
                    }

                    // log
                    expired_time = expired_time.substr(0, expired_time.find("\n"));
                    proxy_log << request_id << ": " << "in cache, but expired at " << expired_time << std::endl;

                    // re-validate
                    std::string response = communicate_with_server(revalidation_request, url, method, protocol, req);
                    if (response.empty()) {
                        delete req;
                        return;
                    }

                    std::string status_code = response.substr(response.find(" ") + 1, 3);

                    if (status_code == "304") { // cache contents not modified
                        send_data(cache_item->response, req->sockfd);

                        // log
                        std::string msg = (cache_item->response).substr(0, cache_item->response.find("\r\n"));
                        proxy_log << req->id << ": Responding " << msg << std::endl;

                        cache->update_time(url);
                        cache->set_age(url, 0); // reset cache_item age
                    }
                    else if (status_code[0] == '2') { // cache contents need to be updated
                        send_data(response, req->sockfd);

                        // log
                        std::string msg = response.substr(0, response.find("\r\n"));
                        proxy_log << req->id << ": Responding " << msg << std::endl;

                        int validation_type = get_validation_type(response, req->id);

                        if (validation_type == NO_STORE) {
                            cache->remove(url);
                        }
                        else { // update cache_item
                            cache_item = create_cache(response, validation_type, req->id);
                            cache->put(url, cache_item);
                        }
                    }
                    else { // response indicates error, warning or note when updating cache, get message for updating cache from server
                        // log
                        std::string msg = response.substr(0, response.find("\r\n"));
                        if (status_code[0] == '4') {
                            proxy_log << req->id << ": ERROR " << msg << std::endl;
                        }
                        else if (status_code[0] == '5') {
                            proxy_log << req->id << ": ERROR " << msg << std::endl;
                        }
                        else if (status_code[0] == '3') {
                            proxy_log << req->id << ": WARNING " << msg << std::endl;
                        }
                        proxy_log << req->id << ": Responding " << msg << std::endl; // log
                        send_data(response, req->sockfd);
                    }
                }
                else { // not stale
                    // log
                    proxy_log << request_id << ": " << "in cache, valid" << std::endl; // log
                    cache->set_age(url, cur_seconds - cache_item->cache_time); // update cache_item age
                    
                    // log
                    std::string msg = (cache_item->response).substr(0, cache_item->response.find("\r\n"));
                    proxy_log << req->id << ": Responding " << msg << std::endl;
                    send_data(cache_item->response, req->sockfd);
                }

                if (close(req->sockfd) == -1) {
                    perror("client socket close() failed");
                }
            }
        }
    }
    else if (method == "POST") {
        std::string post_response = communicate_with_server(original_request, url, method, protocol, req);
        std::string status_code = post_response.substr(post_response.find(" ") + 1, 3);

        if (post_response.empty()) {
            delete req;
            return;
        }

        std::string msg = post_response.substr(0, post_response.find("\r\n"));
        
        if (status_code[0] == '3') {
            proxy_log << req->id << ": WARNING " << msg << std::endl;
        }
        else if (status_code[0] == '4') {
            proxy_log << req->id << ": ERROR " << msg << std::endl;
        }
        else if (status_code[0] == '5') {
            proxy_log << req->id << ": ERROR " << msg << std::endl;
        }

        // log
        proxy_log << req->id << ": Responding " << msg << std::endl;
        send_data(post_response, req->sockfd);

        if (close(req->sockfd) == -1) {
            perror("client socket close() failed");
        }
    }
    else if (method == "CONNECT") {
        https_connect(original_request, request_line, req);
    }
    else {
        std::string Warning_501("HTTP/1.1 501 Not Implemented\r\n\r\n");
        send(req->sockfd, Warning_501.c_str(), Warning_501.length(), 0);

        // log
        proxy_log << req->id << ": WARNING 501 Not Implemented" << std::endl;
    }

    delete req;
}

void Proxy::https_connect(std::string request, std::string request_line, Request *req) {

    std::string headers = request.substr(request.find("\r\n") + 2);
    int host_index = headers.find("Host:") + 6;
    
    std::string hostname = "";
    for (int i = host_index; i < headers.size(); i++) {
        if (headers[i] == '\r') {
            break;
        }
        hostname += headers[i];
    }

    std::string port;
    int colon_index = hostname.find(":");
    if (colon_index == -1) {
        port = "443";        
    } else {
        port = hostname.substr(colon_index+1);
        hostname.erase(colon_index);    
    }
    
    // Connect to server
    int server_socket = server_socket_init(hostname, port, req);
    if (server_socket == -1) {
        return;
    }
    //**** 200 OK reponse to client
    std::string OK_200("HTTP/1.1 200 Connection Established\r\n\r\n");

    if (send(req->sockfd, OK_200.c_str(), OK_200.length(), 0) == -1) {
        perror("send 200 OK back failed");
    }

    //**** Tunnel starts ****
    fd_set readfds;
    struct timeval tv;
    tv.tv_sec = 1;

    while (true) {
        std::vector<char> buf(BUF_SIZE);
        FD_ZERO(&readfds);
        FD_SET(req->sockfd, &readfds);
        FD_SET(server_socket, &readfds);
        int s = select(FD_SETSIZE, &readfds, NULL, NULL, &tv);
        int len;
        if (s == 0) {   
            break;
        }
        else if (FD_ISSET(req->sockfd, &readfds)) {
            len = recv(req->sockfd, &buf.data()[0], BUF_SIZE, 0);
            if (len < 0) {
                perror("Failed to recv from client in tunnel:");
                break;
            } else if (len == 0) {
                break;
            }

            len = send(server_socket, buf.data(), len, 0);
            if (len < 0) {
                perror("Failed to send to server in tunnel:");
                break;
            }
        } 
        else if (FD_ISSET(server_socket, &readfds)) {
            len = recv(server_socket, &buf.data()[0], BUF_SIZE, 0);
            if (len < 0) {
                perror("Failed to recv from server in tunnel:");
                break;
            } else if (len == 0) {
                break;
            }

            len = send(req->sockfd, buf.data(), len, 0);
            if (len < 0) {
                perror("Failed to send to client in tunnel:");
                break;
            }
        }
        
        buf.clear();
    }
    close(server_socket);
    close(req->sockfd);

    // log
    proxy_log << req->id << ": Tunnel closed" << std::endl;
}

std::string Proxy::communicate_with_server(std::string request, std::string absolute_url, std::string method, std::string protocol, Request *req) {
    
    std::string request_headers = request.substr(request.find("\r\n") + 2); // all http headers
    std::string host = get_http_header(request, "Host");
    
    host = host.substr(host.find("Host") + 6); // HTTP Host header without "\r\n", ex: "www.example.com:8080"

    // get relative url
    std::string relative_url = absolute_url.substr(absolute_url.find(host) + host.size()); // ex: "/index.html"

    //Re-write the request line with relative url
    std::string new_request_line = method + " " + relative_url + " " + protocol + "\r\n";
    std::string new_request = new_request_line + request_headers;

    // get server host and port
    size_t colon_index = host.find(":");
    std::string port;
    if (colon_index == std::string::npos) { //default server port if unspecified
        if (method == "CONNECT") // HTTPS
            port = "443"; 
        else // HTTP
            port = "80"; 
    }
    else { // port specified by client
        port = host.substr(colon_index + 1);
        host.erase(colon_index); // remove port num to get pure hostname
    }

    int server_socket = server_socket_init(host, port, req);
    if (server_socket == -1) {
        return "";
    }

    // log
    std::string request_line = method + " " + relative_url + " " + protocol;
    proxy_log << req->id << ": Requesting " <<  request_line <<  " from " <<  host << std::endl;
    
    const char *new_request_buf = new_request.c_str();
    if (send(server_socket, new_request_buf, strlen(new_request_buf) + 1, 0) == -1) {
        perror("Failed to send request to server");
    }

    std::string response = receive_data(BUF_SIZE, server_socket); // Receive response

    std::string response_line = response.substr(0, response.find("\r\n"));

    // log
    proxy_log << req->id << ": Received " <<  response_line <<  " from " <<  host << std::endl;

    if (close(server_socket) == -1) {
        print_error_message("Failed to close() server socket");
    }

    return response;
}

int Proxy::server_socket_init(std::string host, std::string port, Request *req) {
    struct addrinfo hints, *res, *p;
    int status;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_CANONNAME;

    if ((status = getaddrinfo(host.c_str(), port.c_str(), &hints, &res)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));

        std::string ERROR_404("HTTP/1.1 404 Not Found\r\n\r\n");
        if (send(req->sockfd, ERROR_404.c_str(), ERROR_404.length(), 0) == -1) {
            perror("send 404 Error failed");
        }

        // log
        proxy_log << req->id << ": ERROR HTTP/1.1 404 Not Found" << std::endl;
        proxy_log << req->id << ": Responding HTTP/1.1 404 Not Found" << std::endl;

        return -1;
    }

    int server_socket;
    for (p = res; p != NULL; p = p->ai_next) {
        server_socket = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (server_socket == -1) {
            perror("socket() failed");
            continue;
        }

        if (connect(server_socket, p->ai_addr, p->ai_addrlen) == -1) {
            perror("connect() failed");
            if (close(server_socket) == -1) {
                perror("close() failed");
            }
            continue;
        }

        // Connect to the first struct node(a server socket) that works in the LinkedList
        break;
    }

    if (p == nullptr) {
        // std::cerr << "Looped thru LinkedList, but failed to connect to te server" << std::endl;
        
        std::string ERROR_400("HTTP/1.1 400 Bad Request\r\n\r\n");
        if (send(req->sockfd, ERROR_400.c_str(), ERROR_400.length(), 0) == -1) {
            perror("send 400 Error failed");
        }

        // log
        proxy_log << req->id << ": ERROR HTTP/1.1 400 Bad Request" << std::endl;
        proxy_log << req->id << ": Responding HTTP/1.1 400 Bad Request" << std::endl;

        return -1;
    }

    freeaddrinfo(res);
    return server_socket;
}

int Proxy::get_validation_type(std::string response, int request_id) {

    #if TEST_NO_CACHE
    return NO_STORE;
    #endif

    std::string cache_control = get_http_header(response, "Cache-Control");
    std::string e_tag = get_http_header(response, "ETag");
    std::string last_modified = get_http_header(response, "Last-Modified");

    // log
    if (!cache_control.empty()) {
        proxy_log << request_id << ": NOTE " << cache_control << std::endl;
    }
    
    if (!e_tag.empty()) {
        proxy_log << request_id << ": NOTE " << e_tag << std::endl;
    } 
    
    if (!last_modified.empty()) {
        proxy_log << request_id << ": NOTE " << last_modified << std::endl;
    }

    // neither Etag nor Last-Modified
    if (e_tag.empty() && last_modified.empty()) {
        proxy_log << request_id << ": " << "not cacheable because " << "neither Etag nor Last-Modified" << std::endl; // log
        return NO_STORE;
    }

    // no-store
    if (cache_control.find("no-store") != std::string::npos) {
        // do not store cache
        proxy_log << request_id << ": " << "not cacheable because " << "Cache-Control: no-store" << std::endl; // log
        return NO_STORE;
    }

    // private
    if (cache_control.find("private") != std::string::npos) {
        // do not store cache
        proxy_log << request_id << ": " << "not cacheable because " << "Cache-Control: private" << std::endl; // log
        return NO_STORE;
    }

    // no Cache-Control 
    if (cache_control.empty()) {
        return NO_CACHE;
    }
    
    // need revalidation every time
    if (cache_control.find("no-cache") != std::string::npos) {
        return NO_CACHE;
    }

    if (cache_control.find("must-revalidate") != std::string::npos) {
        return MUST_REVALIDATE;
    }

    return NO_STORE;
}

CacheCell* Proxy::create_cache(std::string response, int validation_type, int request_id) {
    CacheCell *cache_item;

    std::string cache_control = get_http_header(response, "Cache-Control"); // Cache-Control header without "\r\n"

    std::string e_tag = get_http_header(response, "ETag"); 
    if (!e_tag.empty()) {
        e_tag = e_tag.substr(e_tag.find(":") + 2); // etag
    }

    std::string last_modified = get_http_header(response, "Last-Modified"); 
    if (!last_modified.empty()) {
        last_modified = last_modified.substr(last_modified.find(":") + 2); // modified-date
    }

    if (validation_type == NO_CACHE) { // new cache (no-cache)
        cache_item = new CacheCell(response, validation_type, e_tag, last_modified);
        proxy_log << request_id << ": " << "cached, but requires re-validation" << std::endl; // log
    }
    else if (validation_type == MUST_REVALIDATE) { // new cache (must-revalidate)
            std::string expires_time = "";

            size_t max_age_index = cache_control.find("max-age");
            if (max_age_index != std::string::npos) { // contains max-age
                int max_age = get_max_age(cache_control, max_age_index);
                cache_item = new CacheCell(response, validation_type, e_tag, last_modified, max_age);
                
                // get expires time
                if (max_age != 0) {
                    time_t expires_seconds = cache_item->cache_time + cache_item->max_age;
                    expires_time = std::string(std::asctime(std::gmtime(&expires_seconds)));
                }
            }
            else { // no max-age, checks the Expires header
                std::string expires = get_http_header(response, "Expires");
                std::string date = get_http_header(response, "Date");

                if (!expires.empty() && !date.empty()) {
                    expires = expires.substr(expires.find("Expires:") + 9); // get time in the Expires header
                    date = date.substr(date.find("Date:") + 6);
                    time_t date_seconds = date_to_seconds(date);
                    time_t expires_seconds = date_to_seconds(expires);

                    cache_item = new CacheCell(response, validation_type, e_tag, last_modified, date_seconds, expires_seconds);
                    expires_time = std::string(std::asctime(std::gmtime(&expires_seconds)));
                }
                else { // lacks max-age, Date and Expires fields, change cache type to no-cache
                    cache_item = new CacheCell(response, validation_type, e_tag, last_modified);
                }
            }

            // log
            if (!expires_time.empty()) {
                expires_time = expires_time.substr(0, expires_time.find("\n"));
                proxy_log << request_id << ": " << "cached, but expires at " << expires_time << std::endl;
            }
            else { // no-cache or (neither max-age nor Expires)
                proxy_log << request_id << ": " << "cached, but requires re-validation" << std::endl;
            }
    }

    return cache_item;
}

int Proxy::get_max_age(std::string cache_control, int index) {
    std::string tmp = cache_control.substr(index + 8);

    // get the value of max-age
    for (int i = 0; i < tmp.size(); i++) {
        if (tmp[i] == '\r' || tmp[i] == ',') {
            tmp = substring(tmp, 0, i - 1);
        }
    }

    return std::stoi(tmp);
}

std::time_t Proxy::date_to_seconds(std::string date) {
    struct tm t;
    std::time_t seconds;

    if (strptime(date.c_str(), "%a, %d %b %Y %H:%M:%S", &t) == NULL) {
        std::cerr << "strptime failed" << std::endl;
    }
    else {
        t.tm_isdst = -1;
        seconds = mktime(&t);
        if (seconds != -1) return seconds;
    }

    return -1;
} 

std::string Proxy::receive_data(int buf_size, int source_sockfd) {
    std::string data = "";
    int data_size = 0;
    //std::vector<char> buf(buf_size);
    while (true) {
        char buf[buf_size];
        int byte_count = recv(source_sockfd, buf, buf_size, 0);
        if (byte_count == -1) {
            print_error_message("recv() failed");
        }
        // The server closed the connection
        if (byte_count == 0) {
            break;
        }
        
        // Append the part of the response that was just received 
        data.append(buf, byte_count);
        data_size += byte_count;
    }

    // if (data_size == 0) {
    //     std::cerr << "The source did not send any data, thread will exit." << std::endl;
    //     pthread_exit(NULL);
    // }
    return data;
}

void Proxy::send_data(std::string data, int destination_sockfd) {

    int bytes_total = data.size();
    int bytes_left = bytes_total;
    int bytes_sent = 0;
    int bytes_count;
    //const char *msg = data.data();
    char *buf = new char[bytes_left];
    memcpy(buf, data.data(), bytes_left);

    while (bytes_sent < bytes_total) {
        bytes_count = send(destination_sockfd, buf + bytes_sent, bytes_left, 0);
        
        if (bytes_count == -1) {
            print_error_message("send() failed");
        }
        
        bytes_sent += bytes_count;
        bytes_left -= bytes_count;
    }

    delete [] buf;
}

std::string Proxy::substring(std::string s, int start, int end) {
    return s.substr(start, end - start + 1);
}

std::string Proxy::get_http_header(std::string r, std::string header_field) {
    std::string headers = r.substr(0, r.find("\r\n\r\n") + 4);

    size_t header_index = headers.find(header_field);
    if (header_index == std::string::npos) {
        return "";
    }
    else {
        std::string tmp = headers.substr(header_index);
        return tmp.substr(0, tmp.find("\r\n"));
    }
}

void Proxy::print_error_message(const char *msg) {
    perror(msg);
}
