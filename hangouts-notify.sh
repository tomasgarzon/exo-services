#!/bin/bash

export TARGET_NAME=$1

curl --request POST \
    --url 'https://chat.googleapis.com/v1/spaces/AAAAqG9ExQI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=ZPX6J8erzun-5a9jaquNgasBvjbeXHmrc16zkXIbMCI%3D' \
    --header 'Content-Type: application/json' \
    --data "{\"text\": \"- https://${TARGET_NAME}.releases.exolever.com\n- https://${TARGET_NAME}ano.releases.exolever.com\"}"
