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

apt install -y python3.11
if [ $? -eq 0 ]; 
    then echo "python3.11 installed successfully" 
else
    echo "!!! Something went wrong with python3.11 installation !!!"
    exit
fi

apt install -y python3.11-dev
if [ $? -eq 0 ]; 
    then echo "python3.11-dev installed successfully" 
else
    echo "!!! Something went wrong with python3.11-dev installation !!!"
    exit
fi

apt install -y python3.11-distutils 
if [ $? -eq 0 ]; 
    then echo "python3.11-distutils installed successfully" 
else
    echo "!!! Something went wrong with python3.11-distutils installation !!!"
    exit
fi

apt install -y python3-pip
if [ $? -eq 0 ]; 
    then echo "python3-pip installed successfully" 
else
    echo "!!! Something went wrong with python3-pip installation !!!"
    exit
fi

curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
if [ $? -eq 0 ]; 
    then echo "pip dependency for python3.11 installed successfully" 
else
    echo "!!! Something went wrong with pip dependency for python3.11 installation !!!"
    exit
fi