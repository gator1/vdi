
cp ~/vdi/horizon to a directory such as ~/test_horizon. Not mandatory but you 
want to have an original copy from git

go to ~/test_horizon/openstack_dashboard/local  to modify local_settings.py
change to where openstack is. 

OPENSTACK_HOST = "192.168.253.162"
VDI_URL = "192.168.253.162:9090/v1.0"


cp -r ~/vdi/vdi_dashboard/vdidashboard ~/test_horizon/openstack_dashboard/dashboards/vdi

modify a sample file to make ~/test_horizon/openstack_dashboard/enabled/_50_vdi.py

we need to modify all the reference to vdidashboard to openstack_dashboard.dashboards.vdi with case and whole word, this needs to check in. 

~/test_horizon/tools$ python install_venv.py to install  horizon and it also build .vent env

""""
 Openstack development environment setup is complete.

     Openstack development uses virtualenv to track and manage Python
         dependencies while in development and testing.

       To activate the Openstack virtualenv for the extent of your current shell
                 session you can run:

                     $ source /home/jim/test_horizon/.venv/bin/activate

       Or, if you prefer, you can run commands in the virtualenv on a case by case
                             basis by running:

                                 $ /home/jim/test_horizon/tools/with_venv.sh <your command>

                                     Also, make test will automatically use the virtualenv.
       """"


       install vdi client
       /home/jim/test_horizon/tools/with_venv.sh pip install -e ~/vdi/python_vdiclient/

       chmod 600 .secret_key_store at ~/test_horizon/openstack_dashboard/local


       :change user.py at ~/test_horizon/.venv/local/lib/python2.7/site-packages/openstack_auth
