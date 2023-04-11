#!/bin/sh

pip_packages=$(python3 -m pip freeze | cut -d'=' -f1)

while read pkg_name; do
    if echo "${pip_packages}" | grep -i -q "${pkg_name}"; then
        python3 -m pip install -r requirements.txt
        return
    fi
done < requirements.txt

python3 main.py
