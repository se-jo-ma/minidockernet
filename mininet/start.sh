echo 'Installing Mininet'
/mininet/util/install.sh -nfv
echo 'Mininet Installed'
echo 'Spinning up Linux Bridge'
sudo brctl addbr br0
sudo brctl addif br0 eth0
sudo ifconfig br0 up
sudo ip link set br0 up
sudo brctl show
echo 'Built Linux Bridge'
echo 'Starting Mininet Project'
python3 /root/sanjose.py