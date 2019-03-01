#ifndef __PROXY_H__
#define __PROXY_H__

#define NO_STORE 0
#define NO_CACHE 1
#define MUST_REVALIDATE 2

#define BUF_SIZE 2097152

class Proxy {
    private:
        int request_id;
        int port;
        int sockfd;
        Cache *cache;
    
    public:
        Proxy(int port, int cache_capacity);
        ~Proxy();

        void socket_init();
        void start();
        void process_request(Request *request);
        std::string communicate_with_server(std::string request, std::string absolute_url, std::string method, std::string protocol, Request *req);
        int server_socket_init(std::string host, std::string port, Request *req);
        void https_connect(std::string request, std::string request_line, Request *req);
        int get_validation_type(std::string response, int request_id);
        CacheCell* create_cache(std::string response, int validation_type, int request_id);
        int get_max_age(std::string cache_control, int index);

        std::string receive_data(int buf_size, int source_sockfd);
        void send_data(std::string data, int destination_sockfd);

        std::string substring(std::string s, int start, int end);
        std::string get_http_header(std::string r, std::string header_field);
        std::time_t date_to_seconds(std::string date);
        void print_error_message(const char *msg);
};

#endif