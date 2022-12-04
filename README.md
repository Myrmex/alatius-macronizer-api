# Alatius Macronizer Flask API

- [Alatius Macronizer Flask API](#alatius-macronizer-flask-api)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
  - [Preparation](#preparation)
    - [PostgreSql](#postgresql)
      - [PostgreSql Account](#postgresql-account)
    - [Flask](#flask)
  - [Dockerization](#dockerization)
    - [Create Container](#create-container)
    - [Prepare](#prepare)
    - [Build](#build)
    - [Database](#database)
    - [Cleanup](#cleanup)
    - [API](#api)
    - [Build Image](#build-image)

>This software is part of a project that has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation program under grant agreement No. 101001991.

## Overview

Docker image:

>pull vedph2020/macronizer

This project contains the logic for building a raw dockerized version of the [Alatius macronizer](https://alatius.com/macronizer/). This excellent macronizer by Johan Winge is essentially based on Python running on top of C tools like [RFTagger](http://www.cis.uni-muenchen.de/~schmid/tools/RFTagger/) and [Latin dependency treebank](http://www.dh.uni-leipzig.de/wo/projects/ancient-greek-and-latin-dependency-treebank-2-0/). It also provides an Apache based web page on top of its engine, but what is really needed for projects requiring to integrate it is a web API, so that any software client, whatever its language, can take advantage of that functionality. Sure, that may not be the optimal way of integrating software components; but certainly is one of the simplest.

Once you have a Docker image wrapping the macronizer, all its software dependencies, and its PostgreSQL database, it becomes much easier to consume its functionality: you just have to add a layer to your Docker stack, and consume the API endpoint for macronization.

The API I created is a minimalist thin layer on top of macronizer. Its only purpose is getting some text to be macronized, and replying with the result. There is no need for authentication or authorization logic, as this API is made to be consumed by upper layers which eventually provide it. In my scenario, I have an ASP.NET 7 web API consuming this service from a Docker compose stack, and exposing it to the outer world in the context of a set of services protected by JWT-based authentication.

The API uses JSON and consists of two endpoints:

- `GET /test` just returns a constant JSON object with a single string property named `result`; it can be used for diagnostic purposes to test if the API itself is running.
- `POST /macronize` posts a Latin text and gets its macronized version. Its _input_ is a JSON object with this schema (all the properties are optional unless stated otherwise):
  - `text` (string, required): the text to macronize.
  - `maius` (boolean): include/exclude capitalized words.
  - `utov` (boolean): convert U to V.
  - `itoj` (boolean): convert I to J.
  - `ambigs` (boolean): mark ambiguous lengths.
The _output_ object has these properties:
  - `result` (string): the resulting text.
  - `error` (string): the error message, if any.
  - `maius`, `utov`, `itoj`, `ambigs`: the parameters as received in the POST request.

Given its essential nature, the API has been implemented with [Flask](https://flask.palletsprojects.com/), using [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/) to serve it.

To create the Docker image, I followed the "manual" approach: start from a base image, modify it configuring everything for running macronizer, add the API on top of it, and then commit the modified Docker container into a new image. That's not the optimal way of building it, whence its size; but this represents a first stage, which can later be refined. My first objective was getting something working in a reasonable timeframe, to provide better integration of macronizer functionalities for a research tool built on top of my Chiron metrical analysis system (see e.g. [part 1](http://www.libraweb.net/articoli3.php?chiave=202106501&rivista=65&articolo=202106501004) and [part 2](http://www.libraweb.net/articoli3.php?chiave=202106502&rivista=65&articolo=202106502004) of my latest paper about it), targeting late antique prose rhythm, in the context of the [ERC Consolidator Grant "AntCoCo"](https://www.uni-bamberg.de/en/erc-cog-antcoco/the-project/) lead by prof.dr.dr.dr. Peter Riedlberger.

Currently, the alpha image I got from this process is tagged `vedph2020/macronizer` in the Docker Hub.

## Quick Start

To quickly play with the API:

1. ensure you have [installed Docker](https://github.com/vedph/cadmus_doc/blob/master/deploy/docker-setup.md) on your computer.
2. download [docker-compose.yml](docker-compose.yml) from this repository into some folder. Ensure that you download this as a plain text (YAML) file, rather than as the source code of the GitHub HTML page.
3. open a terminal window in that folder, and enter command:

```bash
docker compose up
```

This is for Docker compose V2. If you are still on V1, use the non-plugin syntax, i.e. `docker-compose up` (mind the dash). Remember to prefix `sudo` for Linux/OSX.

The macronizer API should now be reachable at `localhost:51234`. You can test it is there with `localhost:51234/test`.

To macronize some text, you must post a JSON object representing it at `localhost:51234/macronize`. For instance, here is a sample request:

```txt
POST http://localhost:51234/macronize HTTP/1.1
Content-Type: application/json
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Cache-Control: no-cache
Postman-Token: 9b15a31c-7d14-4bba-ae96-859813f0bf07
Host: localhost:51234
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Content-Length: 64

{
    "text": "Nil sine magno vita labore dedit mortalibus."
}
```

Response:

```txt
HTTP/1.1 200 OK
Content-Length: 88
Content-Type: application/json
Date: Fri, 06 May 2022 10:59:08 GMT
Server: waitress

{"result":"N\u012bl sine magn\u014d v\u012bt\u0101 lab\u014dre dedit mort\u0101libus."}
```

In Linux you could do like this:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"quos putamos amissos, praemissi sunt."}' localhost:51234/macronize
```

## Preparation

Before even starting to work on the Docker image, I had to check all the setup passages, and make sure that they work seamlessly in a Linux environment. First, I created a fresh Ubuntu VM (20.04) to play with.

>Note: if you want to avoid [gcc issues](https://github.com/Alatius/latin-macronizer/issues/22), use Ubuntu 20.04. Later Ubuntu releases have compilation problem, which require some patches to be addressed, until the main repository is patched.

To start with, in the Ubuntu user's home, create a `Documents/macron` directory. Then, enter this `macron` directory and clone the macronizer repository:

```bash
cd ~/Documents
mkdir macron
cd macron
git clone https://github.com/Alatius/latin-macronizer.git
```

Then, essentially there are 3 setup steps:

1. setup PostgreSql.
2. setup macronizer following the original [instructions](https://github.com/Alatius/latin-macronizer/blob/master/INSTALL.txt).
3. setup Flask API.

### PostgreSql

Quick setup instructions can be found e.g. here:

- [Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart)
- [Ubuntu 21](https://www.linuxhelp.com/how-to-install-postgresql-on-ubuntu-21-04)
- [Ubuntu 22](https://linuxconfig.org/ubuntu-22-04-postgresql-installation)
- to remove before installing: `sudo apt-get remove --purge postgresql-13` (use your version number).

Note: once installed, by default PostgreSQL Server will start up automatically each time the system boots. To disable this behavior, you can enter:

```bash
 sudo systemctl disable postgresql
 ```

and then use `enable` to enable it back.

So, at first I install PostgreSql (this is required for those distros or Docker base images without it):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service
```

(you can specify version like ... `install postgresl-14`).

To check if the database service is running (<https://askubuntu.com/questions/50621/can-not-connect-to-postgresql-listening-on-port-5432>:

```bash
netstat -nlp | grep 5432
```

If you don't find it, use this command to find its endpoint:

```bash
netstat -lp --protocol=unix | grep postgres
```

It's typical to use port 5432 if it is available. If it isn't, most installers will choose the next free port, usually 5433. To connect to a specific port (eventually add `-h localhost -U postgres`):

```bash
psql -p 5433
```

#### PostgreSql Account

This is a reminder for those not acquainted with PostgreSql, summarized from [this page](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart).

Postgres uses a concept called “roles” to handle authentication and authorization. These are, in some ways, similar to regular Unix-style users and groups. After installation, Postgres is configured to use `ident` authentication, meaning that it associates Postgres roles with a matching Unix/Linux _system account_. If a role exists within Postgres, a Unix/Linux username with the same name is able to sign in as that role. This is why there is no default password for the default `postgres` user.

The installation procedure created a user account called `postgres` that is associated with the default Postgres role. There are a few ways to utilize this account to access Postgres:

(a) one way is to switch over to the `postgres` account on your server by running the following command:

```bash
sudo -i -u postgres
```

Now you can just type `psql` to access the client (use `\q` to quit). To return to the regular system user, type `exit`.

(b) Another way to connect to the Postgres prompt is to run the psql command as the postgres account directly with `sudo`:

```bash
sudo -u postgres psql
```

This will log you directly into Postgres without the intermediary bash shell in between.

Once you login as `postgres` (method a), create a new role:

```bash
createuser --interactive
```

You can see the script from this project for a non interactive version.

### Flask

Useful links:

- [Flask API tutorial](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
- [Flask setup](https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask)

To develop the API skeleton I used a trivial macronizer's mock you can find at `macronizer.py` in this project. In the Linux VM you can fire the API using the real macronizer tool, e.g. with a [curl POST](https://linuxize.com/post/curl-post-request/) like:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"quos putamos amissos, praemissi sunt"}' localhost:105/macronize
```

## Dockerization

Here I recap the procedure for creating the Docker image. As macronizer requires to compile C files, execute Python scripts, and connect to a PostgreSql database, I chose the official PostgreSql image as my base.

### Create Container

First you create a `postgres` container and fire `bash` in it:

```ps1
# this is based on Debian GNU/Linux 11 (bullseye) (cat /etc/os-release)
docker run --name macronizer -d -e POSTGRES_PASSWORD=postgres postgres
docker exec -it macronizer /bin/bash
```

In it, you can enter the psql console with `psql --username postgres`.

>Note: each of the following steps assumes that you are located in the last location of the previous step. It is like a unique sh file, but I split the commands into sections to make them more readable. You can find the full script at [build.sh](build.sh).

### Prepare

- start location: `/`

Prepare folder `/usr/local/macronizer` and install prerequisites.

```bash
cd /usr/local
mkdir macronizer
cd macronizer
apt-get update
apt-get install git python3 python-is-python3 build-essential libfl-dev python3-psycopg2 unzip wget -y
```

### Build

- start location: `/usr/local/macronizer`

Download repositories is not enough, as the original repository has some minor issues with `gcc` versions. Rather than forking the repository for very few changes, I just collected the files requiring a patch in a ZIP, used to overwrite the files from the original repository. Should the original repository be patched, the script will be simplified.

You can find the ZIP file in this repository. Essentially, it contains these fixes:

- all the `makefile`'s where changed to receive the option `-fcommon` in `CFLAGS`
- comment `gk_string Gstr;` at line 6 of `countendtables.c`.

```bash
git clone https://github.com/Alatius/latin-macronizer.git
cd latin-macronizer
git clone https://github.com/Alatius/morpheus.git
# patch before making:
# we need to overwrite selected files, i.e. all the makefile
# plus gkends/countendtables.c which must comment out #6 gk_string Gstr.
# I placed the patch files in a temporary location and use wget to fetch them
cd morpheus
wget http://fusisoft.it/xfer/morpheus-src.zip
unzip -o morpheus-src.zip
rm morpheus-src.zip
cd src
# morpheus/src
make
make install
cd ..
./update.sh
./update.sh
# this is to test
echo "salve" | MORPHLIB=stemlib bin/cruncher -L
cd ..
git clone https://github.com/Alatius/treebank_data.git
wget https://www.cis.uni-muenchen.de/~schmid/tools/RFTagger/data/RFTagger.zip
unzip RFTagger.zip
cd RFTagger/src
make
make install
cd ../..
./train-rftagger.sh
```

### Database

- start location: `/usr/local/macronizer`

Use `psql` to create a new user and a database:

```bash
psql --username postgres -c "create user theusername password 'thepassword';" -c "create database macronizer encoding 'UTF8' owner theusername;"
```

Initialize the database:

```bash
python macronize.py --initialize
# for testing
python macronize.py --test
```

### Cleanup

- start location: `/usr/local/macronizer`

```bash
rm -Rf RFTagger treebank_data
```

### API

- start location: `/usr/local/macronizer`

Put `api.py` in the `latin_macronizer` folder (this is from `api-production.py`), and then install its dependencies (see also <https://code.visualstudio.com/docs/python/tutorial-flask>):

```bash
# I got api.py from a temporary location as this repo did not yet exist
wget http://fusisoft.it/xfer/api.py
apt-get install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install flask
python -m pip install waitress
```

You can test with `python api.py`.

### Build Image

To build the image from the container as modified in the preceding sections (see [here](https://stackoverflow.com/questions/29015023/docker-commit-created-images-and-entrypoint)), enter the folder where you downloaded this repository in your host machine and type a command similar to this:

1. `docker commit macronizer vedph2020/macronizer-base` to commit container's changes into an image.
2. `docker build . -t vedph2020/macronizer:0.0.2-alpha` to build the image using [Dockerfile](Dockerfile).

>Note: playing with containers will quickly eat a lot of disk space in the host. In Windows, you can reclaim it later:

1. locate the VHDX file for Docker WSL, usually somewhere like `C:\Users\dfusi\AppData\Local\Docker\wsl\data`.
2. close Docker desktop from its icon and run `wsl --shutdown`.
3. run (replace `USERNAME` with your Windows user name):

```ps1
optimize-vhd -Path C:\Users\USERNAME\AppData\Local\Docker\wsl\data\ext4.vhdx -Mode full
```

You can also [move the VHDX](https://github.com/docker/for-win/issues/7348).

Happy coding!

Daniele Fusi
