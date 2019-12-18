#!/bin/bash

coverage run --source='.' manage.py test
echo " ###############################"
echo " #     End coverage script     #"
echo " ###############################"
coverage html
echo " ###############################"
echo " #       HTML report done!     #"
echo " ###############################"
