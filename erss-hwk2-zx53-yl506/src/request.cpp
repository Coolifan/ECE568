#include "common.h"
#include "request.h"

Request::Request(int sockfd, std::string from_ip, std::string request_time, int id) {
    this->sockfd = sockfd;
    this->from_ip = from_ip;
    this->request_time = request_time;
    this->id = id;
}

Request::Request(const Request &req) {
    sockfd = req.sockfd;
    from_ip = req.from_ip;
    request_time = req.request_time;
    id = req.id;
}

