# brainwave
Project Management tool.


### to run the application

uvicorn main:app --reload


### added as service to systemctl

$ sudo nano /etc/systemd/system/brainwave.service

-------------------------------------------

[Unit]
Description=Project Management FastAPI App
After=network.target

[Service]
User=YOURUSER
Group=YOURUSER

WorkingDirectory=/home/YOURUSER/brainwave

Environment="PATH=/home/YOURUSER/venv_py/bin"

ExecStart=/home/YOURUSER/venv_py/bin/uvicorn main:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

-------------------------------------------

$ sudo systemctl daemon-reexec
$ sudo systemctl daemon-reload
$ sudo systemctl start brainwave

$ sudo systemctl enable brainwave

$ systemctl status brainwave


