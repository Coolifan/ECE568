#ifndef __REQUEST_H__
#define __REQUEST_H__

class Request {
    public:
        int sockfd;
        std::string from_ip;
        std::string request_time;
        int id;
        
        Request();
        Request(int sockfd, std::string from_ip, std::string request_time, int id);
        Request(const Request &req);
};

#endif