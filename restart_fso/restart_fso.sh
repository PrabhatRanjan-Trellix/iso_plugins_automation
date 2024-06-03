source "$iso_plugins_automation/config/config.sh"

docker start rabbitmq
# start httpd server
docker exec -d "${docker_container}" bash -c "httpd -D FOREGROUND"

cd $ui_code_path && yarn start &

# Run the fso api server
docker exec -it "${docker_container}" bash -c "\
    sh /vagrant/setup/dev_init.sh"
