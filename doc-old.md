# Building Macronizer Flask API - Old Procedure

## Testing the Solution

Before even starting to work on the Docker image, I had to check all the setup passages, and make sure that they work seamlessly in a Linux environment. Then, I added the Python scripts for the Flask API, and ensured that they worked as expected.

The quickest way for doing it for me was creating a fresh Ubuntu VM (20.04) to play with. Having a true VM rather than a Docker container is easier at this stage, because everything is already there, and we can start with the same environment used by the macronizer itself.

>Note: to avoid [gcc issues](https://github.com/Alatius/latin-macronizer/issues/22), use Ubuntu 20.04. Later Ubuntu releases have compilation problem, which require some patches to be addressed, until the main repository is patched. Also, a full-fledged Unix distro is of course far from ideal as an image base; yet, starting from a more streamlined image would imply consuming much more time in adjusting the setup procedure.

In the Ubuntu VM we only work with the terminal. So, open a terminal window and in the Ubuntu user's home create a `Documents/macron` directory (any other will do anyway). Then, enter this `macron` directory and clone the macronizer repository:

```bash
cd ~/Documents
mkdir macron
cd macron
git clone https://github.com/Alatius/latin-macronizer.git
```

>When doing this in the Ubuntu Docker container, you will probably have to install git: `apt install git`.

Then, essentially there are 3 setup steps:

1. setup PostgreSql.
2. setup macronizer following the original [instructions](https://github.com/Alatius/latin-macronizer/blob/master/INSTALL.txt).
3. setup the wrapper Flask API.

### Installing PostgreSql

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

#### Note on PostgreSql Account

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

### Adding Flask API

Useful links:

- [Flask API tutorial](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
- [Flask setup](https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask)

To develop the API skeleton I used a trivial macronizer's mock you can find at `macronizer.py` in this project. In the Linux VM you can fire the API using the real macronizer tool, e.g. with a [curl POST](https://linuxize.com/post/curl-post-request/) like:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"quos putamos amissos, praemissi sunt"}' localhost:105/macronize
```

## Creating the Docker Image

Once tested the FlasK API in the Ubuntu VM, it's time to package everything in a Docker image.

As macronizer requires to compile C files, execute Python scripts, and connect to a PostgreSql database, I chose the official PostgreSql image as my base. This anyway has the disadvantage that, unless using older images, we will have to deal with issues in compiling C, as macronizer relies on Ubuntu 20, whereas newer PostgreSql images use later versions of the OS.

### Creating the Docker Container

First you create a `postgres` container (here I name it `macronizer`) and fire `bash` in it:

```ps1
# this is based on Debian GNU/Linux 11 (bullseye) (cat /etc/os-release)
docker run --name macronizer -d -e POSTGRES_PASSWORD=postgres postgres
docker exec -it macronizer /bin/bash
```

In it, you can enter the psql console with `psql --username postgres`.

>Note: each of the following steps assumes that you are located in the last location of the previous step. It is like a unique `sh` file, but I split the commands into sections to make them more readable. You can find the full script at [build.sh](build.sh).

### Preparing the Build Environment

- 📁 start location: `/`

Create a folder `/usr/local/macronizer` where we will install source code to compile, and install prerequisites.

```bash
cd /usr/local
mkdir macronizer
cd macronizer
apt-get update
apt-get install git python3 python-is-python3 build-essential libfl-dev python3-psycopg2 unzip wget -y
```

### Building Macronizer Code

- 📁 start location: `/usr/local/macronizer`

Downloading the above repositories is not enough, as the original code has some minor issues with `gcc` versions. Rather than forking the repository for very few changes, I just collected the files requiring a patch in a ZIP, used to overwrite the files from the original repository. Should the original repository be patched, the script will be simplified.

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

### Creating Macronizer Database

- 📁 start location: `/usr/local/macronizer`

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

### Cleaning Up

- 📁 start location: `/usr/local/macronizer`

```bash
rm -Rf RFTagger treebank_data
```

### Adding the API

- 📁 start location: `/usr/local/latin-macronizer`

Put `api.py` in the `latin_macronizer` folder (this is [api-production.py](api-production.py) renamed as `api.py`), and then install its dependencies (see also <https://code.visualstudio.com/docs/python/tutorial-flask>):

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

You can test if the API works by running it with `python api.py`.

### Building the Image

To build the image from the container as modified in the preceding sections (see [here](https://stackoverflow.com/questions/29015023/docker-commit-created-images-and-entrypoint)), enter the folder where you downloaded this repository in your host machine and type a command similar to this:

1. `docker commit macronizer vedph2020/macronizer-base` to commit container's changes into an image. The container name here is `macronizer`. If you changed the name, use your own.
2. `docker build . -t vedph2020/macronizer:0.0.4-alpha` to build the image using [Dockerfile](Dockerfile). Use your own Docker Hub repository, here I'm using `vedph2020`.

>Note: playing with containers will quickly eat a lot of disk space in the host. In Windows, you can try to reclaim it later:

1. locate the VHDX file for Docker WSL, usually somewhere like `C:\Users\dfusi\AppData\Local\Docker\wsl\data`.
2. close Docker desktop from its icon and run `wsl --shutdown`.
3. run (replace `USERNAME` with your Windows user name):

```ps1
optimize-vhd -Path C:\Users\USERNAME\AppData\Local\Docker\wsl\data\ext4.vhdx -Mode full
```

You can also [move the VHDX](https://github.com/docker/for-win/issues/7348).
