# Assignment #2 Danger Log

## HTTP methods not implemented

In this homework, we just implemented GET, POST and CONNECT methods. So when our proxy receives other HTTP methods, such as HEAD or PUT, we send 501 Not Implemented back to the client to avoid further problems.

## `getaddrinfo()` ERROR or DNS failure

Some servers sometimes may not provide an available host to serve the requests, or the DNS resolver fails to resolve a domain name. In these cases, we traverse the linked list returned from `getaddrinfo`. If none of the hosts can be used for HTTP connection, we return a special value to raise the exception to the calling function. Then the upper-level function will release all the memory allocated and end the process.

## implicit port in url

Sometimes, within the url of a request's `Host` header, the server port is not provided. Our proxy will check the server port before forwarding the request. We add the default port for common service, 80 for HTTP and 443 for HTTPS.

## empty contents in the transmission

We use a loop to send and receive data in order to get complete data flow. However, sometimes we find empty contents in some transmission processes. If we get empty content, it will not be counted as a valid request or response and will be abandoned. As a result, server/client will not crash due to empty requests/responses.

## different HTTP status codes

Aside from common http response, such as 200 or 304 or 502, we also handled some other kinds of responses. When the url cannot be found, our proxy will send 404 NOT FOUND. When we receive methods not implemented in this homework, 501 Not Implemented is sent back to the client.

## cache updates

We implemented a thread-safe LRU cache in this assignment. The renew of cache is a very complicated process. We designed a data structure to record the type and some necessary information for each cache item. Our proxy will check the headers related to cache everytime the cache requires an update from the original server in order to avoid the frequent change of cache's type. For example, a cache item for a certain url may be must-revalidate type at first (requires re-validation if expired). However, in later updates, its cache type may change to no-store (in this case, we need to remove it from the cache) or no-cache (requires re-validation every time).

We have very robust functions to deal with the cache update logic. We check if some related headers (like ETag, Last-Modified, Date, Expires) in necessary circumstances. We also store an age value in our cache item's class for a faster and more complete check of cache expirations.

In some cases, `max-age` can be zero and sometimes `max-age` is absent. Then we check if there are `Date` and `Expires` headers, or there exists `ETag` or `Last-Modified` headers that still can be used for re-validation.

## memory management

We use some C++11 STL features and data structures and are ver y cautious about creating objects with `new` (sometimes multiple objects in a container data structure). We release memory in threads functions and destructors in time to avoid possible memory leak or too much use of memory.