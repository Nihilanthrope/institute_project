import socket
print("=== PORT SCANNER ===")
target = (input("Enter Your Target Ip :"))
Port = int(input("Enter Your Target Port :"))

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex((target, Port))
if result == 0:
    print("Port is OPEN")
else:
    print("Port is CLOSED or not reachable")

s.close()