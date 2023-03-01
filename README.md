# A-simple-messaging-app-in-Python

## Introduction
This project is an assignment for the ELEC-C7420, Principles of Networking course at Aalto University. The main goal is to make a simple messaging app to practice socket programming. The project was implemented using Python and PyQt was used for the GUI.

**The core features of the app:**
- Direct messaging between clients
  - Client can add other users to their conversation list.
  - Client can select what user he/she wants to send the message to.
  - The server delivers messages to the specified user as requested by the client.
- Group messaging
  - Client can create a group.
  - The owner of the group can add/remove members from the group.
  - The owner can rename the group.
  - The server will forward the messages sent to the group to every member of said group.
- Offline messaging
  - Sender is informed if the receiver is offline and when the receiver was online last time.
  - Messages sent to an offline client will be buffered on the server and forwarded to the client once he/she go online again.
- Other features
  - Message display timestamp, sender, and the group (if it is a group message).
  - Check if the receiver has read your message or not.
  - Simutaneous connection of multiple clients.
  - Support both IPv4 and IPv6
- (Bonus feature) File transfer
  - Files of any format can be sent through the app.
  - The receiver is notified whenever someone sent them a file. They can view the information (name and size) of the file.
  - The receiver can decide if he/she wants to receive or discard the file.
- Voluntary extra features 
  - (somewhat) User-friendly and intuitive UI.
  - Send message by clicking Enter after the user finished typing.
  - Dedicated message box and conversation view.
  - Selecting active conversation with the mouse.

**Assignment Outcome:** 20/20 points + 2 Bonus points. Overall, I am quite happy with how the project turned out. I was able to learn a lot from this project and build something fun.
  
## Application Walk-through
![UI Image](./Documentation/Photo%20gallery/UI%20design/rough%20UI%20design.png)
