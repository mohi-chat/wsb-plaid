#!/usr/bin/env bash

sudo kill -9 $(sudo netstat -tulnp | grep :3000 | awk '{print $7;}' | grep -o -E '[0-9]+')