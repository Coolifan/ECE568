#include "common.h"
#include "request.h"
#include "cache.h"
#include "proxy.h"

std::ofstream proxy_log;

int main(void) {
    // log.open(LOG_PATH, std::ios_base::app | std::ios_base::out);
    proxy_log.open(LOG_PATH, std::ios_base::out);

    /**
     * Usage:
     * Proxy(<port>, <cache_capacity>)
     * the cache capacity is the maximum number of unique 
     * request urls you want to keep in the cache 
     */
    Proxy proxy(12345, 100);
    proxy.socket_init();
    proxy.start();
    proxy_log.close();
    
    return EXIT_SUCCESS;
}