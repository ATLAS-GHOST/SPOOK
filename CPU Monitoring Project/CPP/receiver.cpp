#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <chrono>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
    
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    
    // Set receive buffer
    int buffer_size = 2147483647;
    setsockopt(sock, SOL_SOCKET, SO_RCVBUF, (char*)&buffer_size, sizeof(buffer_size));
    
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9009);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    bind(sock, (sockaddr*)&addr, sizeof(addr));
    std::cout << "UDP PORT 9000: LISTENING" << std::endl;
    
    char buffer[65536];
    uint64_t packets_received = 0;
    auto start = std::chrono::steady_clock::now();
    
    while (true) {
        int len = recvfrom(sock, buffer, sizeof(buffer), 0, nullptr, nullptr);
        
        if (len == 4 && memcmp(buffer, "STOP", 4) == 0) {
            break;
        }
        
        packets_received++;
    }
    
    auto end = std::chrono::steady_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();
    double pps = packets_received / seconds;
    double mbps = (16 * pps * 8) / 1000000.0;
    
    std::cout << "\nPackets received: " << packets_received << std::endl;
    std::cout << "Time elapsed: " << seconds << "s" << std::endl;
    std::cout << "PPS: " << pps << std::endl;
    std::cout << "Mbps: " << mbps << std::endl;
    
    closesocket(sock);
    WSACleanup();
    return 0;
}