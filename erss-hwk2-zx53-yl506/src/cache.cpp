#include "common.h"
#include "cache.h"

// CacheCell
CacheCell::CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified): response(res), size(res.length()), validation_type(validationType), e_tag(eTag), last_modified(lastModified) {
    cache_time = std::time(nullptr);
}

CacheCell::CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified, int max_age): response(res), size(res.length()), validation_type(validationType), e_tag(eTag), last_modified(lastModified) {
    cache_time = std::time(nullptr);
    this->max_age = max_age;

    if (max_age == 0) {
        this->validation_type = NO_CACHE;
    }
}

CacheCell::CacheCell(std::string res, int validationType, std::string eTag, std::string lastModified, std::time_t date, std::time_t expires_date): response(res), size(res.length()), validation_type(validationType), e_tag(eTag), last_modified(lastModified) {
    cache_time = std::time(nullptr);
    this->date = date;
    this->expires_date = expires_date;
}

bool CacheCell::isExpired(std::time_t cur) {
    if (max_age != -1) {
        if (max_age > age) return false;
        else return true;
    }
    else if (expires_date - date > age) {
        return false;
    }

    return true;
}


// Cache
Cache::Cache(int capacity): size(capacity) {
    std::unique_lock<std::mutex> lock(mtx);
}

Cache::~Cache() {
    for (auto cell: kv_store) {
        delete cell.second;
    }
}

CacheCell* Cache::get(std::string url) {
    mtx.lock();
    if (kv_store.count(url) == 0) {
        // print();
        mtx.unlock();
        return nullptr;
    }
        
    update(url);
    // print();
    mtx.unlock();
    return kv_store[url];
}

void Cache::put(std::string url, CacheCell *cell) {
    mtx.lock();

    if (kv_store.size() == size && kv_store.count(url) == 0) {
        pop();
    }
    update(url);
    kv_store[url] = cell;
    // print();
    mtx.unlock();
}

void Cache::remove(std::string url) {
    mtx.lock();

    // log
    proxy_log << "(no-id) " << "removed " <<  cache.back() << " from cache due to Cache-Control: no-store" << std::endl;
    map.erase(cache.back());
    kv_store.erase(cache.back());
    delete kv_store[cache.back()];
    cache.pop_back();

    mtx.unlock();
}

void Cache::set_age(std::string url, int value) {
    mtx.lock();

    kv_store[url]->age = value;

    mtx.unlock();
}

void Cache::update_time(std::string url) {
    mtx.lock();

    kv_store[url]->cache_time = std::time(nullptr);

    mtx.unlock();   
}

void Cache::update(std::string url) {
    if (kv_store.count(url)) {
        cache.erase(map[url]);
    }

    cache.push_front(url);
    map[url] = cache.begin();
}

void Cache::pop() {
    // log
    proxy_log << "(no-id) " << "evicted " <<  cache.back() << " from cache" << std::endl;

    map.erase(cache.back());
    delete kv_store[cache.back()];
    kv_store.erase(cache.back());
    cache.pop_back();
}

void Cache::print() {
    std::cout << "cache:" << std::endl;
    for (auto url: cache) {
        std::cout << url << "; " << std::endl;
    }

    std::cout << "map:" << std::endl;
    for (auto loc: map) {
        std::cout << loc.first << "; " << std::endl;
    }

    std::cout << "kv-store:" << std::endl;
    for (auto item: kv_store) {
        std::cout << item.first << ": " << item.second << "; " <<std::endl;
    }
}
