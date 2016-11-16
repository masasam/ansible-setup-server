# ansible-vps
My vps server's ansible  

## ホスト側準備
ホストは Arch Linux なので  

    pacman -S ansible
	cd git
	git clone git@github.com:masasam/ansible-vps.git

#### ゲスト側準備
ゲストも Arch Linux なので

	pacman -Sy bash-completion openssh
	
arch linux(centos8)は python3 がデフォルトなので

	pacman -Sy python2

ansible で利用する user を作成

    useradd -m -G wheel -s /bin/bash ansible
	su - ansible
	cd .ssh/
	ssh-keygen -t rsa -b 4096	
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys

root に戻って

	systemctl start sshd
