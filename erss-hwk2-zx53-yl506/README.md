# HW2 - HTTP Web Caching Proxy

## Authors: 

 Yifan Li, yl506@duke.edu
 
 Zi Xiong, zx53@duke.edu

## Instructions:


To run the app: 
1. Clone the repo, `git clone https://gitlab.oit.duke.edu/yl506/erss-hwk2-zx53-yl506.git`
2. Open the project directory, `cd erss-hwk2-zx53-yl506`
3. Run `sudo docker-compose build && sudo docker-compose up`
4. Connect to the running proxy with port number 12345.

## Key Features:

- **Well-designed LRU cache**

We combined a linked list with two hash maps to integrate our cache. The cache is able to handle *access*, *push*, and *pop* actions in **O(1)** time.

**NOTE**: we initialized the cache size (the number of unique URLs that are cached) to be 100. You can modify this in `main()` if needed.

- **Extensive validation info and error info checking**

Many header fields related to cache control, including *ETag*, *Last-Modified*, *max-age*, *age*, *Expires*, and *Date*, are examined to determine whether
the revalidation actions (conditional requests) are needed and whether the cache needs to be updated. 
Also, given the fact that there are so many things related to cache control/revalidation and we have limited time to read rfc 
documents, we made an assumption that we would consider a website as `Cache-Control: no-cache` if certain header fields are missing within the 
response and that causes some confusion. And we would consider a website as `Cache-Control: no-store` if no common header fields are present.

Also, a few common error codes related to corrupted responses are handled separately, such as *404 Not found* and *501 Not implemented*. 

Check our danger log for detailed discussions.

- **Clean code with OO design**

There are 4 classes defined in our code: `Proxy`, `Cache`, `CacheCell`, and `Request`. Specifically, the `Proxy` class contains all the functions needed for the 
HTTP connection workflow, the `Cache` class contains functions used for cache operations, the `CacheCell` class stores the detailed information about a 
cache webpage, and the `Request` class stores the information about the HTTP request made within the thread, such as request id.

Our `main()` function first create a `Proxy` object, and only calls 2 functions later: `Proxy::socket_init()` which creates the socket to connect to the
client, binds the socket and starts listening, and `Proxy::start()` that activates the daemon process and creates a new thread whenever a new request is
accepted. We use the `std::thread` from C++11 to achieve concurrency.


## Extra notes:

Also we are confident that our proxy is able to handle most of the common requests, our implementation is definitely not perfect. Please restart the
proxy if you happen to "freeze" our proxy by trying some great corner cases, and feel free to let us know if you have any questions about our program.
Thanks!




