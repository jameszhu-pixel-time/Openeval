import socket
import multiprocessing as mp, time, socket, sys
def port_is_open(host: str, port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex((host, port)) == 0

def wait_port(host: str, port: int, timeout=30) -> bool:
    for _ in range(timeout):
        if port_is_open(host, port):
            return True
        time.sleep(1)
    return False