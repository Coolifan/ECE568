all: link

request: request.cpp
	g++ -std=c++11 -g -c request.cpp -o request.o

cache: cache.cpp
	g++ -std=c++11 -pthread -g -c cache.cpp -o cache.o

proxy: proxy.cpp
	g++ -std=c++11 -pthread -g -c proxy.cpp -o proxy.o

main: main.cpp
	g++ -std=c++11 -g -c main.cpp -o main.o

link: request cache proxy main
	g++ -std=c++11 -pthread -g request.o cache.o proxy.o main.o -o proxy

test: link
	./proxy

clean:
	rm -rf *.o *.~ proxy

