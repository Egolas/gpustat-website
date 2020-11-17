# Monitor website for GPU statistics

## Features
- Show current GPU usage of every server.
    - auto refresh every `5s`.
- Show GPU usage in `24 hours` / `1 week` / `all time`

## Requests
- flask
- mysql
- mysql-connector-python
- [gpu-statistics][gpu-statistics-link]

## Deployment
1. Edit `host_names` and `database_config` in `app.py` (not necessary for `reporter.py`, in which it's just used for debug)
2. Edit `dirpath` in `gpustat-website.service` and `gpustat-website.sh`
3. Set `gpustat-website.sh` runable,
> sudo chmod +x ./gpustat-website.sh
4. Copy `gpustat-website.service` to `/lib/systemd/system`
> sudo cp  ./gpustat-website.service /lib/systemd/system
5. Enable system service
> sudo systemctl enable gpustat-website.service

[gpu-statistics-link]: https://github.com/Egolas/gpu-statistics