#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <chrono>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
    
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9009);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    
    // Set send buffer
    int buffer_size = 2147483647;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, (char*)&buffer_size, sizeof(buffer_size));
    
    char packet[16] = {0};
    uint64_t seq = 0;
    
    auto start = std::chrono::steady_clock::now();
    auto end = start + std::chrono::seconds(10);
    
    while (std::chrono::steady_clock::now() < end) {
        memcpy(packet, &seq, sizeof(seq));
        sendto(sock, packet, sizeof(packet), 0, (sockaddr*)&addr, sizeof(addr));
        seq++;
    }
    
    // Send stop signal
    const char* stop = "STOP";
    sendto(sock, stop, 4, 0, (sockaddr*)&addr, sizeof(addr));
    
    auto elapsed = std::chrono::steady_clock::now() - start;
    double seconds = std::chrono::duration<double>(elapsed).count();
    double pps = seq / seconds;
    double mbps = (16 * pps * 8) / 1000000.0;
    
    std::cout << "Packets sent: " << seq << std::endl;
    std::cout << "Time elapsed: " << seconds << "s" << std::endl;
    std::cout << "PPS: " << pps << std::endl;
    std::cout << "Mbps: " << mbps << std::endl;
    
    closesocket(sock);
    WSACleanup();
    return 0;
}