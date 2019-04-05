# OpenCV Remote Video Processing

1.  - `local.py` hosts a http server (default `localhost:5050`) for streaming local webcam's video using `vlc` subprocess.
    - Then open a socket connection to listen from a remote server (default `localhost:5052`).
2.  - `remote.py` captures video from remote http address `localhost:5050`.
    - Then sends the data back to the client socket opened with address `localhost:5052`

## Commands:
1.  ```
    python local.py \
    --stream-host=127.0.0.1 \
    --stream-port=5050 \
    --server-host=127.0.0.1 \
    --server-port=5052
    ```
2. ```
    python remote.py \
    --stream-host=127.0.0.1 \
    --stream-port=5050 \
    --server-host=127.0.0.1 \
    --server-port=5052
    ```
        
## Requirements

1. `pip install opencv-python`
2. `pip install numpy`
3.  `sudo apt install vlc`