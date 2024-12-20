import socket
import threading
import argparse
from datetime import datetime
import sys
import queue

class PortScanner:
    def __init__(self, target, start_port=1, end_port=1024, thread_count=100, timeout=1):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.thread_count = thread_count
        self.timeout = timeout
        self.queue = queue.Queue()
        self.open_ports = []
        
    def scan_port(self):
        while True:
            try:
                port = self.queue.get_nowait()
            except queue.Empty:
                break
                
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    service = "Unknown"
                    try:
                        service = socket.getservbyport(port)
                    except:
                        pass
                    self.open_ports.append((port, service))
                    print(f"\033[92m[+] Port {port} is open - Service: {service}\033[0m")
                
                sock.close()
                
            except socket.error:
                pass
            
            finally:
                self.queue.task_done()
                
    def run_scan(self):
        try:
            # Resolve target IP
            target_ip = socket.gethostbyname(self.target)
            print(f"\n[*] Starting scan on host: {self.target} ({target_ip})")
            print(f"[*] Time started: {datetime.now()}\n")
            
            # Fill queue with ports
            for port in range(self.start_port, self.end_port + 1):
                self.queue.put(port)
            
            # Start threads
            thread_list = []
            for _ in range(self.thread_count):
                thread = threading.Thread(target=self.scan_port)
                thread_list.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in thread_list:
                thread.join()
            
            print("\n[*] Scan completed!")
            print(f"[*] Total open ports found: {len(self.open_ports)}")
            
            return self.open_ports
            
        except socket.gaierror:
            print("\n[!] Hostname could not be resolved")
            sys.exit()
            
        except KeyboardInterrupt:
            print("\n[!] Scan canceled by user")
            sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Python Port Scanner")
    parser.add_argument("target", help="Target host to scan")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=float, default=1, help="Timeout in seconds (default: 1)")
    
    args = parser.parse_args()
    
    scanner = PortScanner(
        args.target,
        args.start,
        args.end,
        args.threads,
        args.timeout
    )
    
    scanner.run_scan()

if __name__ == "__main__":
    main()
