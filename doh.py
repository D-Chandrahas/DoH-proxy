import socket
import requests as req
from threading import Thread
# from dnslib import DNSRecord

SEV_ADDR = ("127.1.1.1", 53)


# def log(dns_req_pack, dns_res_pack):
#     dns_req = DNSRecord.parse(dns_req_pack)
#     dns_res = DNSRecord.parse(dns_res_pack)
#     for i in dns_req.questions: print(i)
#     print('-' * 20, len(dns_res_pack), '-' * 20)
#     for i in dns_res.rr: print(i)
#     for i in dns_res.auth: print(i)
#     for i in dns_res.ar: print(i)
#     print('=' * 100)


def udp_request_handler(sock, data, addr):
    res = req.post("https://1.1.1.1/dns-query", data=data, headers={"accept": "application/dns-message", "content-type": "application/dns-message"})
    sock.sendto(res.content, addr)
    # log(data, res.content)


def start_udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(SEV_ADDR)

    try:
        while True:
            try:
                data, addr = server.recvfrom(512)
                # udp_request_handler(server, data, addr)
                handle_udp_request = Thread(target=udp_request_handler, args=(server, data, addr))
                handle_udp_request.start()
            except ConnectionResetError as e:
                # print("\x1b[31m", e, "\x1b[0m", '\n', '=' * 100, sep='')
                pass
    finally:
        server.close()


if __name__ == "__main__":
    start_udp_server()

