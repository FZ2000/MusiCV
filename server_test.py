import socket

sock_server = socket.socket()

sock_server.bind(('', 12345))

sock_server.listen(5)

while True:
   # Establish connection with client.
   c, addr = sock_server.accept()
   print('Got connection from', addr)

   # send a thank you message to the client.
   c.send(b'Thank you for connecting')
   # Close the connection with the client
   c.close()