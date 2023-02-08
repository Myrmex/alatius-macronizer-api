# Alatius Macronizer Flask API

- [Alatius Macronizer Flask API](#alatius-macronizer-flask-api)
  - [Overview](#overview)
  - [Usage](#usage)

>This software is part of a project that has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation program under grant agreement No. 101001991. I thank Johan Winge for his help in troubleshooting issues.

👉 This is a thin Python (Flask) based API for macronizer. See the [ASP.NET based API](https://github.com/Myrmex/macronizer-api) for a full API.

## Overview

🐋 Docker image (0.1.3):

>pull vedph2020/macronizer

This project contains the logic for building a raw dockerized version of the [Alatius macronizer](https://alatius.com/macronizer/). This excellent macronizer by Johan Winge is essentially based on Python running on top of C tools like [RFTagger](http://www.cis.uni-muenchen.de/~schmid/tools/RFTagger/) and [Latin dependency treebank](http://www.dh.uni-leipzig.de/wo/projects/ancient-greek-and-latin-dependency-treebank-2-0/). It also provides an Apache based web page on top of its engine, but what is really needed for projects requiring to integrate it is a web API, so that any software client, whatever its language, can take advantage of that functionality. Sure, that may not be the optimal way of integrating software components; but certainly is one of the simplest.

Once you have a Docker image wrapping the macronizer, all its software dependencies, and its PostgreSQL database, it becomes much easier to consume its functionality: you just have to add a layer to your Docker stack, and consume the API endpoint for macronization.

The API I created is a minimalist thin layer on top of macronizer. Its only purpose is getting some text to be macronized, and replying with the result. There is no need for authentication or authorization logic, as this API is made to be consumed by upper layers which eventually provide it. For a full API, please refer to [my ASP.NET macronizer API](https://github.com/Myrmex/macronizer-api). In my scenario, I have an ASP.NET 7 web API consuming this service from a Docker compose stack, and exposing it to the outer world in the context of a set of services protected by JWT-based authentication.

The API uses JSON and consists of two **endpoints**:

- `GET /test` just returns a constant JSON object with a single string property named `result`; it can be used for diagnostic purposes to test if the API itself is running.
- `POST /macronize` posts a Latin text and gets its macronized version. Its _input_ is a JSON object with this schema (all the properties are optional unless stated otherwise):
  - `text` (string, required): the text to macronize.
  - `maius` (boolean): whether to mark with macrons words like _maius_ (=/majjus/).
  - `utov` (boolean): convert U to V.
  - `itoj` (boolean): convert I to J.
  - `ambigs` (boolean): mark ambiguous lengths.
The _output_ object has these properties:
  - `result` (string): the resulting text.
  - `error` (string): the error message, if any.
  - `maius`, `utov`, `itoj`, `ambigs`: the parameters as received in the POST request.

Given its essential nature, the API has been implemented with [Flask](https://flask.palletsprojects.com/), using [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/) to serve it.

To create the Docker image, I followed the "manual" approach: start from a base image; modify it configuring everything for running macronizer; add the API on top of it; and finally commit the modified Docker container into a new image. That's not the optimal way of building it, whence its size; but this represents a first stage, which can later be refined. My first objective was getting something working in a reasonable timeframe, to provide better integration of macronizer functionalities for a research tool built on top of my Chiron metrical analysis system (see e.g. [part 1](http://www.libraweb.net/articoli3.php?chiave=202106501&rivista=65&articolo=202106501004) and [part 2](http://www.libraweb.net/articoli3.php?chiave=202106502&rivista=65&articolo=202106502004) of my latest paper about it), targeting late antique prose rhythm, in the context of the [ERC Consolidator Grant "AntCoCo"](https://www.uni-bamberg.de/en/erc-cog-antcoco/the-project/) lead by prof.dr.dr.dr. Peter Riedlberger.

Currently, the alpha image I got from this process is tagged `vedph2020/macronizer` in the Docker Hub.

>Note: the API is written with Flask, thus using Python. You can find it in the image folder `/opt/latin-macronizer` in the file `api.py` when you enter the container's bash shell via a command like `docker exec -it CONTAINER_ID /bin/bash`.

## Usage

👉 To quickly play with the macronizer API service:

1. ensure you have [installed Docker](https://github.com/vedph/cadmus_doc/blob/master/deploy/docker-setup.md) on your computer.
2. download [docker-compose.yml](docker-compose.yml) from this repository into some folder. Ensure that you download this as a plain text (YAML) file, rather than as the source code of the GitHub HTML page.
3. open a terminal window in that folder, and enter this command:

```bash
docker compose up
```

>This is for Docker compose V2. If you are still on V1, use the non-plugin syntax, i.e. `docker-compose up` (mind the dash). Remember to prefix `sudo` for Linux/MacOS.

The macronizer API should now be reachable at `localhost:51234`. You can test it is there with `localhost:51234/test`.

To macronize some text, you must post a JSON object representing it at `localhost:51234/macronize`. For instance, here is a sample **request**:

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

The corresponding **response**:

```txt
HTTP/1.1 200 OK
Content-Length: 88
Content-Type: application/json
Date: Fri, 06 May 2022 10:59:08 GMT
Server: waitress

{"result":"N\u012bl sine magn\u014d v\u012bt\u0101 lab\u014dre dedit mort\u0101libus."}
```

The **endpoints** you can test are:

- `test` endpoint:

```bash
curl http://localhost:51234/test -H "Accept: application/json"
```

- `macronize` endpoint: the input JSON body is like `{ text: string, maius?: boolean, utov?: boolean, itoj?: boolean, ambigs?: boolean}`; the output is like `{ result: string, error?: string }`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"rursus imperium propagamus.","ambigs":true}' http://localhost:51234/macronize
```

Happy coding!

Daniele Fusi
