#!/usr/bin/env python3
"""
ZION Pool Protocol Test
Testuje protokol našeho ZION poolu
"""

import socket
import json
import time

def test_zion_pool_protocol():
    pool_host = '91.98.122.165'
    pool_port = 3335
    
    print(f"🔍 Testuje ZION Pool protokol na {pool_host}:{pool_port}")
    
    try:
        # Připojení k poolu
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((pool_host, pool_port))
        print("✅ Úspěšně připojeno k poolu")
        
        # Test 1: Stratum protokol (XMRig standard)
        print("\n📡 Test 1: Stratum login protocol")
        stratum_login = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "login",
            "params": {
                "login": "ZionTestWallet123",
                "pass": "x",
                "agent": "XMRig/6.22.2"
            }
        }
        
        message = json.dumps(stratum_login) + '\n'
        print(f"📤 Odesílám: {message.strip()}")
        sock.send(message.encode())
        
        # Čekání na odpověď
        time.sleep(2)
        
        try:
            response = sock.recv(1024).decode()
            print(f"📥 Odpověď: {response}")
        except socket.timeout:
            print("⏰ Timeout - žádná odpověď")
        
        # Test 2: Jednoduchý JSON protokol  
        print("\n📡 Test 2: Simple JSON protocol")
        simple_msg = {"method": "mining.subscribe", "id": 1}
        message2 = json.dumps(simple_msg) + '\n'
        print(f"📤 Odesílám: {message2.strip()}")
        sock.send(message2.encode())
        
        time.sleep(2)
        try:
            response2 = sock.recv(1024).decode()
            print(f"📥 Odpověď: {response2}")
        except socket.timeout:
            print("⏰ Timeout - žádná odpověď")
            
        # Test 3: Raw text protokol
        print("\n📡 Test 3: Raw text protocol")
        raw_msg = "HELLO ZION POOL\n"
        print(f"📤 Odesílám: {raw_msg.strip()}")
        sock.send(raw_msg.encode())
        
        time.sleep(2)
        try:
            response3 = sock.recv(1024).decode()
            print(f"📥 Odpověď: {response3}")
        except socket.timeout:
            print("⏰ Timeout - žádná odpověď")
        
        sock.close()
        print("✅ Test dokončen")
        
    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    test_zion_pool_protocol()