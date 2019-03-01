#ifndef __CACHE_H__
#define __CACHE_H__

#define NO_CACHE 1
#define MUST_REVALIDATE 2

class CacheCell {
    public:
        std::string response;
        int size;
        std::time_t cache_time;
        std::string e_tag;
        std::string last_modified;

        // for expiration check
        int max_age = -1;
        int age = 0;
        time_t date = -1;
        time_t expires_date = -1;

        /**
         * type code:
         * 1 - revalidate on every request
         * 2 - revalidate only if stale
         */
        int validation_type;
    
        CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified);
        CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified, int max_age);
        CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified, std::time_t date, std::time_t expires_date);

        bool isExpired(std::time_t cur);
};

class Cache {
    public:
        int size = 1000000;

        Cache();
        Cache(int capacity);
        ~Cache();

        CacheCell* get(std::string url);
        void put(std::string url, CacheCell *cell);
        void remove(std::string url);
        void set_age(std::string url, int value);
        void update_time(std::string url);
        void print();

    private:
        std::list<std::string> cache;
        std::unordered_map<std::string, std::list<std::string>::iterator> map;
        std::unordered_map<std::string, CacheCell*> kv_store;
        // pthread_mutex_t lock;
        std::mutex mtx;

        void update(std::string);
        void pop();
};

#endif