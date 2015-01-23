echo "create database vdi" | mysql -uroot -pstackdb
tox -evenv -- vdi-db-manage --config-file etc/vdi/vdi.conf upgrade head
