chmod +x setup.sh
apt-get update
apt-get install -y build-essential=12.8ubuntu1
apt-get install default-libmysqlclient-dev=1.0.8 -y
apt-get clean
rm /var/lib/apt/lists/*
chmod +x setup.sh
./setup.sh
pip3 install -r --no-cache-dir requirements.txt