Simple HTTP POST to XMPP MUC bot
================================

Build with:

     docker build -t bot:1 .

Start with:

    docker run --rm -it -p 8880:80 -e JID=bot@example.com -e PASSWORD=password -e ROOM=room@conference.example.com -e NICK=bot bot:1

Send message:

    curl -i -X POST -d message=haha http://localhost:8880/robot

