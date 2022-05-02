# Alatius Macronizer Flask API

- [Alatius Macronizer Flask API](#alatius-macronizer-flask-api)
  - [Preparation](#preparation)
  - [PostgreSql](#postgresql)
    - [Account](#account)
  - [Flask](#flask)
  - [Testing in Host](#testing-in-host)

## Preparation

To start with, in your Ubuntu user home create `macron` under `Documents`. Then, enter this `macron` directory and clone the macronizer repository: `git clone https://github.com/Alatius/latin-macronizer.git`.

To setup the host:

Note: use Ubuntu 20.04. For some reason, 21 or 22 give errors during the make process.

1. setup PostgreSql.
2. setup macronizer: [instructions](https://github.com/Alatius/latin-macronizer/blob/master/INSTALL.txt).
3. setup Flask.

## PostgreSql

Note: once installed, by default PostgreSQL Server will start up automatically each time your system boots. If you’d like to change this behavior, you can always modify it with this command:

```bash
 sudo systemctl disable postgresql
 ```

 (use `enable` to enable it back).

 Instructions:

- [Ubuntu 21](https://www.linuxhelp.com/how-to-install-postgresql-on-ubuntu-21-04)
- [Ubuntu 22](https://linuxconfig.org/ubuntu-22-04-postgresql-installation)
- [Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart)
- to remove before installing: `sudo apt-get remove --purge postgresql-13` (use your version number)

The following refers to Ubuntu 20.

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service
```

(you can specify version like ... `install postgresl-14`).

Check if service is running (<https://askubuntu.com/questions/50621/can-not-connect-to-postgresql-listening-on-port-5432>:

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

### Account

By default, Postgres uses a concept called “roles” to handle authentication and authorization. These are, in some ways, similar to regular Unix-style users and groups.

Upon installation, Postgres is set up to use `ident` authentication, meaning that it associates Postgres roles with a matching Unix/Linux _system account_. If a role exists within Postgres, a Unix/Linux username with the same name is able to sign in as that role. This is why there is no default password for the default `postgres` user.

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

## Flask

- [Flask API tutorial](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
- [Flask setup](https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask)

Flask setup: in the macron folder:

```bash
sudo apt install python3-virtualenv
virtualenv flask
cd flask
source bin/activate
sudo apt install python3-pip
pip install Flask
pip install waitress
```

## Testing in Host

In a host with the macronizer command prepared:

1. copy the `api.py` file (not `macronizer.py`, which is just a mock).
2. edit the copied `api.py` to make these changes:
   1. comment out `from macronizer import Macronizer`.
   2. uncomment it after `sys.path.append`.
3. launch `python api.py`
4. test with a [curl POST](https://linuxize.com/post/curl-post-request/) like:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"quos putamos amissos, praemissi sunt"}' localhost:105/macronize
```
