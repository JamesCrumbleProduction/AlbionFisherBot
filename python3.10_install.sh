#!/bin/bash


if [ "$EUID" -ne 0 ]
  then echo "Please run as root (sudo)"
  exit
fi

add-apt-repository ppa:deadsnakes/ppa -y && apt update
if [ $? -eq 0 ]; 
    then echo "apt python repository added and updated successfully" 
else
    echo "!!! Something went wrong on adding and updating python repo !!!"
    exit
fi

apt install -y python3.10
if [ $? -eq 0 ]; 
    then echo "python3.10 installed successfully" 
else
    echo "!!! Something went wrong with python3.10 installation !!!"
    exit
fi

apt install -y python3.10-dev
if [ $? -eq 0 ]; 
    then echo "python3.10-dev installed successfully" 
else
    echo "!!! Something went wrong with python3.10-dev installation !!!"
    exit
fi

apt install -y python3.10-distutils 
if [ $? -eq 0 ]; 
    then echo "python3.10-distutils installed successfully" 
else
    echo "!!! Something went wrong with python3.10-distutils installation !!!"
    exit
fi

apt install -y python3-pip
if [ $? -eq 0 ]; 
    then echo "python3-pip installed successfully" 
else
    echo "!!! Something went wrong with python3-pip installation !!!"
    exit
fi

curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
if [ $? -eq 0 ]; 
    then echo "pip dependency for python3.10 installed successfully" 
else
    echo "!!! Something went wrong with pip dependency for python3.10 installation !!!"
    exit
fi