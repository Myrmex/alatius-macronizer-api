# Building Macronizer Flask API

## Overview

This procedure aims at creating a Docker image with a fully configured instance of macronizer, wrapped in a thin Python-based API. In my first attempt to create the image, I started from the PostgreSQL Docker image, because it already provided a configured instance of PostgreSQL, and was optimized to include only those parts of the OS required for this purpose.

Yet, that procedure complicated things because of the different OS version used in the PostgreSQL image, with issues arising in compiling C code. So, I tried with another approach, starting from the same platform macronizer was first developed in, i.e. Ubuntu 20.04. I grabbed the Docker image for that version of the OS, and applied a procedure which essentially follows the instructions provided in the original repository, slightly adapted to the mutated environment. In fact, even though Ubuntu version is 20 as required by the C options used in that source, there are some differences due to the fact that here Ubuntu is running inside a Docker container. Essentially this means that `sudo` there is not meaningful, and that some of the packages are not there. This time, the procedure was nearly identical, because I had to install PostgreSQL too, nor I had to mess with issues arising from the different OS versions in compiling C code.

The only assumption in this procedure for your host machine is to have [Docker installed](https://myrmex.github.io/overview/cadmus/docker-setup/). Once Docker is in place, you can even repeat the whole procedure and it should produce the same result. At any rate, if you want to inspect the macronizer setup it's probably easier to just download the prebuilt image, and enter it, like this:

```bash
docker run -it --name macronizer vedph2020/macronizer:0.1.1 /bin/bash
```

You will then find everything under `/opt/latin-macronizer`.

## Procedure

In my scenario, I run this procedure inside a Ubuntu 20.04 VM with Docker installed. This allows quicker testing and restarting from scratch where required, without polluting my physical machine. So, in the end I have my physical machine hosting a Ubuntu VM, and that Ubuntu VM hosting Docker containers.

(1) run a fresh Ubuntu 20.04 instance and enter its shell:

```bash
docker run -it --name ubuntu ubuntu:20.04 /bin/bash
```

(2) inside the container's shell, follow the instructions at <https://github.com/Alatius/latin-macronizer/blob/master/INSTALL.txt>, as detailed here with the required changes for the mutated environment:

```bash
# added by myself
cd /opt
apt-get update
apt install git
git clone https://github.com/Alatius/latin-macronizer.git
cd latin-macronizer

# instructions from https://github.com/Alatius/latin-macronizer/blob/master/INSTALL.txt
# (removing sudo, and adding apt install where required)
apt install build-essential libfl-dev python3-psycopg2 unzip -y
apt install python-is-python3 -y

git clone https://github.com/Alatius/morpheus.git
cd morpheus/src
make
make install
cd ..
./update.sh
./update.sh
echo "salve" | MORPHLIB=stemlib bin/cruncher -L
cd ..

git clone https://github.com/Alatius/treebank_data.git

apt install wget -y
wget https://www.cis.uni-muenchen.de/~schmid/tools/RFTagger/data/RFTagger.zip
unzip RFTagger.zip
cd RFTagger/src
make
make install
cd ../..

./train-rftagger.sh

apt-get install postgresql
service postgresql start
# check status
service postgresql status
# change to user postgres so we can enter psql
su - postgres
psql
postgres=# create user theusername password 'thepassword';
postgres=# create database macronizer encoding 'UTF8' owner theusername;
postgres=# \q
exit

python macronize.py --initialize
python macronize.py --test
rm -rf RFTagger treebank_data

# add API
wget http://fusisoft.it/xfer/api.py
apt-get install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install flask
python -m pip install waitress
python -m pip install psycopg2-binary
```

(3) Once you have done this, exit the container, and create a base image from it like:

```bash
docker commit CONTAINER_ID vedph2020/macronizer:0.1.1-base
```

Then get into a folder `Dockerfile` and `start.sh`, and generate the image according to the Dockerfile:

```bash
docker build . -t vedph2020/macronizer:0.1.1 -t vedph2020/macronizer:latest
docker push vedph2020/macronizer:0.1.1
```

The image is now complete and ready to be used or pushed into the Docker Hub.

## Testing

You can test the image by running a container from it, with a simple [docker compose script](docker-compose.yml), starting it like `docker compose up`; or via this command: `docker run --name macronizer -p 51234:105 vedph2020/macronizer`.

Once you have started the container, the API endpoint should be reachable from your host machine at `http://localhost:51234`:

- `test` endpoint:

```bash
curl http://localhost:51234/test -H "Accept: application/json"
```

- `macronize` endpoint: the input JSON body is like `{ text: string, maius?: boolean, utov?: boolean, itoj?: boolean, ambigs?: boolean}`; the output is like `{ result: string, error?: string }`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"rursus imperium propagamus.","ambigs":true}' http://localhost:51234/macronize
```
