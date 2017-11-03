#!/usr/bin/env bash

while [ $# -gt 0 ]
do
    case "$1" in
        --)	shift; break;;
        -*)
            echo >&2 \
            "usage: $0 [major,minor,patch]"
            exit 1;;
        *)  break;;	# terminate while loop
    esac
    shift
done

# Navigate to project path
cd $(dirname "$0")

# Bump version
if [[ "$1" =~ "minor" ]] || [[ "$1" =~ "major" ]] || [[ "$1" =~ "patch" ]]
then
    bumpversion $1
    RESULT=$?
else
    echo "error: bump version required."
    echo "usage $0 [major,minor,patch]"
    exit 1
fi

if [ "$RESULT" -eq 0 ]
then
    # Get new version
    VERSION=$(grep -oEi "[0-9]+\.[0-9]+\.[0-9]+" pytest_needle/__init__.py)

    # Release new version
    git push --tags origin master
    python setup.py sdist bdist_wheel
    twine upload dist/*
    RELEASED=$?
else
    echo "Failed to update to version $VERSION"
    exit 1
fi

if [ "$RELEASED" -eq 0 ]
then
    echo "${VERSION} released..."
else
    echo "Unable to release version ${VERSION}"
fi
