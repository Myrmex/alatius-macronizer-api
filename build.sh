#!/bin/bash
cd /usr/local
mkdir macronizer
cd macronizer
apt-get update
apt-get install git python3 python-is-python3 build-essential libfl-dev python3-psycopg2 unzip -y

# build
echo BUILD
apt-get install wget -y
git clone https://github.com/Alatius/latin-macronizer.git
cd latin-macronizer
git clone https://github.com/Alatius/morpheus.git
# patch before making:
# we need to overwrite selected files, i.e. all the makefile
# plus gkends/countendtables.c which must comment out #6 gk_string Gstr
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

# database
echo DATABASE
psql --username postgres -c "create user theusername password 'thepassword';" -c "create database macronizer encoding 'UTF8' owner theusername;"
python macronize.py --initialize
python macronize.py --test

# cleanup
rm -Rf RFTagger treebank_data

# api
wget http://fusisoft.it/xfer/api.py
apt install python3-virtualenv -y
virtualenv flask
cd flask
source bin/activate
pip install Flask
pip install waitress
cd ..
ln -s /usr/local/macronizer/latin-macronizer/api.py /usr/local/bin/macronizer-api
chmod 755 /usr/local/bin/macronizer-api
