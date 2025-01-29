import socket
import requests
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


def doh_request(data):
    return requests.post("https://1.1.1.1/dns-query",
                    data=data,
                    headers={"accept": "application/dns-message",
                             "content-type": "application/dns-message"}
                    ).content


def udp_request_handler(sock, req, addr):
    res = doh_request(req)
    if len(res) > 512:
        # res = res[:512]
        # todo: implement proper truncation
        res = res[:2] + bytes((res[2] | 2,)) + res[3:]
    sock.sendto(res, addr)
    # log(req, res)


def start_udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(SEV_ADDR)

    with server:
        while True:
            try:
                data, addr = server.recvfrom(512)
                handle_udp_request = Thread(target=udp_request_handler, args=(server, data, addr))
                handle_udp_request.start()
            except ConnectionResetError as e:
                # print("\x1b[31m", e, "\x1b[0m", '\n', '=' * 100, sep='')
                pass


def tcp_request_handler(conn):
    req = b""
    with conn:
        # todo: handle pipelined requests
        while pack:=conn.recv(1024):
            req += pack
        conn.sendall(res := doh_request(req))
        # log(req, res)
        

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(SEV_ADDR)
    server.listen()

    with server:
        while True:
            conn, _ = server.accept()
            handle_tcp_request = Thread(target=tcp_request_handler, args=(conn,))
            handle_tcp_request.start()


if __name__ == "__main__":
    udp_server = Thread(target=start_udp_server)
    udp_server.start()
    tcp_server = Thread(target=start_tcp_server)
    tcp_server.start()
    # todo: stopping the server & thread joining
