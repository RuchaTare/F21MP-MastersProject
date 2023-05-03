#!/bin/sh

set -e

image='recipe-bot'
target='tests'

tmp=$(mktemp -d)
chmod 777 "$tmp"

cd $(dirname $0)/..
mkdir -p reports

docker build -t "$image-$target" --target="$target" .
docker run -i --rm \
    --security-opt=seccomp=unconfined \
    -v "$tmp":/alana/reports \
    "$image-$target" \
    "$@"

rm -fr reports/docker-tests/
cp -r "$tmp" ./reports/docker-tests/
rm -fr "$tmp"
