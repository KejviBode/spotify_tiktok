#!/usr/bin/bash

# Enter the list of browsers to be downloaded
firefox_versions=( "86.0" "87.0b3", "113.0.1" )
gecko_drivers=( "0.33.0" )

# Download Firefox
for br in ${firefox_versions[@]}
do
    echo "Downloading Firefox version $br"
    mkdir -p "./opt/firefox/$br"
    curl -Lo "./opt/firefox/$br/firefox-$br.tar.bz2" "http://ftp.mozilla.org/pub/firefox/releases/$br/linux-x86_64/en-US/firefox-$br.tar.bz2"
    tar -jxf "./opt/firefox/$br/firefox-$br.tar.bz2" -C "./opt/firefox/$br/"
    mv "./opt/firefox/$br/firefox" "./opt/firefox/$br/firefox-temp"
    mv ./opt/firefox/$br/firefox-temp/* ./opt/firefox/$br/
    rm -rf "./opt/firefox/$br/firefox-$br.tar.bz2"
done

# Download Geckodriver
for dr in ${gecko_drivers[@]}
do
    echo "Downloading Geckodriver version $dr"
    mkdir -p "./opt/geckodriver/$dr"
    curl -Lo "./opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz" "https://github.com/mozilla/geckodriver/releases/download/v$dr/geckodriver-v$dr-linux64.tar.gz"
    tar -zxf "./opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz" -C "./opt/geckodriver/$dr/"
    chmod +x "./opt/geckodriver/$dr/geckodriver"
    rm -rf "./opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz"
done