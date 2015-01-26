echo "create database vdi" | mysql -uroot -pTest
tox -evenv -- vdi-db-manage --config-file etc/vdi/vdi.conf upgrade head
