# Section 6

- `main.py`: section 6.2, client GUI and websocket client
- `tests/`: section 5 unit tests
  - `test_rx.py`: section 5.1 basic reactive test
  - `test_transaction_form.py`: section 5.2 reactive GUI test
  - `test_server.py`: section 5.3 reactive Tornado server test
- `server/` directory contains code from:
    - `matching_server.py`: section 4.3 web server, section 6.1
      managing orders on the web server
    - `transaction_server.py`: section 5.4 cluster testing
- `client/` directory contains code from:
  - section 3 reactive GUIs and data flows
  - `client.py`: section 4.4 real-time async client receiver/sender
    (used in section 5.4 cluster testing)

Server-side Streams:

* orders per user
* all orders (combination of orders per user)
* prices (aggregate of orders grouped by stock symbol)

Client-side Streams:

* prices (from server)
* orders (from user input or from bot)

Cluster test:

    cd server
    python matching_server.py 8888 &
    python matching_server.py 7777 &
    python transaction_server.py &
    cd ..
    cd client
    python client.py
