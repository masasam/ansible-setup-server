## Preparing the server you want to provision with ansible

Target OS
- Archlinux
- Debian9 stretch
- Centos7

## Synopsis

Create a server from scratch

	ansible-playbook main.yml

Update package inside server

	ansible-playbook update.yml

Write directory names exist under roles you want to use at main.yml

	- hosts: server
		user: "{{ username }}"
		become: yes
		vars:
	   	- include_tasks: vars/server.yml
	   roles:
	    - emacs
		- git
		- nginx
		- python
		- vim
		- zsh
		- less
		- others
		- selenium

That is all.

## When creating a Debian server

Create user to use with ansible as root

	apt-get install python openssh-server zsh bash-completion sudo
	useradd -m -G sudo -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	curl https://github.com/masasam.keys >> ~/.ssh/authorized_keys ← Register public key registered with github

Return to root

	systemctl enable ssh
	systemctl start ssh

Set host name on your laptop or desktop

	hostname debian

visudo

	echo 'ansible ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo

## Install ansible on your laptop or desktop

	pip install --user ansible
	git clone https://github.com/masasam/ansible-setup-server.git

## Perform provisioning by ansible

	ansible-playbook main.yml

Write variables and passwords in group_vars/server.yml
Encrypt server.yml in advance with the following command

	ansible-vault encrypt server.yml

If you write the location of the cryptographic password in
ansible.cfg, you do not have to hit the password each time
(The contents are only the password)

	vault_password_file = ~/Dropbox/ansible/vault_pass

What is in group_vars/server.yml (Write a password etc. here)

	hostname: 'yourhost' ← Linux host name
	domain: 'yourdomain' ← Main domain
	subdomain: 'subdomain.yourdomain' ← sub domain(using blog)
	mydomain: 'mydomain.yourdomain' ← sub domain(using lisp)
	username: 'ansible' ← User name ansible ssh
	mailroot: 'youremailaddress' ← E-mail address to transfer root's mail
	monitalert: 'youremailaddress' ← Destination of alert mail from monit
	infopassword: '1e3396a8ecbc77a4cd81145c2c6b'
	mariadbrootpassword: 'mariadbrootpassword' ← The password of the mariadb root user
	mackerelapikey: 'yourmackerelapikey' ← mackerel's apikey
	dbname: 'yourdbbame' ← DB name used in mariadb
	dbpassword: 'yourdbpassword' ← That password
	docroot: '/home/html' ← Main document route for nginx
	docrootblog: '/home/blog' ← Document root of blog for nginx
	docrootppap: '/home/ppap'
	docrootjekyll: '/home/jekyll'
	docrootjekyll2: '/home/jekyll2'
	docrootlisp: '/home/lisp'

Infopassword will be the password for the email address of info@yourdomain
How to make infopassword

	doveadm pw
	Enter new password: yourpassword
	Retype new password: yourpassword

With

	{CRAM-MD5}913336a8ecba7764cd81245c2c6b

Because it is

	infopassword: '913336a8ecba7764cd81245c2c6b'

#### Update the server only playbook

	ansible-playbook update.yml

## When creating a Debian test container at localhost

	sudo pacman debootstrap
	yaourt -S debian-archive-keyring

	mkdir debian
	sudo debootstrap stretch debian http://ftp.jaist.ac.jp/pub/Linux/debian/

	sudo chroot debian
	passwd root

	sudo systemd-nspawn -b -D ~/debian

From here debian virtual server

	apt-get install python openssh-server zsh bash-completion sudo

	useradd -m -G sudo -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	curl https://github.com/masasam.keys >> ~/.ssh/authorized_keys ← Register public key registered with github

Return to root

	systemctl enable ssh
	systemctl start ssh

Set host name

	hostname debian

vi /etc/hosts

	127.0.0.1       localhost debian

Set up a user (group) that sudo can use

	update-alternatives --config editor

visudo

	echo 'ansible ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo

Set the following in .ssh/config on your laptop or desktop

	Host debiantest
						HostName localhost
						User ansible

Write at main.yml

	- hosts: debiantest

Run playbook

	ansible-playbook main.yml

## When creating a test container for centos at localhost

	yaourt yum
	mkdir centos

	sudo vim /etc/yum/repos.d/centos.repo
	[centos]
	name=centos
	baseurl=http://ftp.jaist.ac.jp/pub/Linux/CentOS/7/os/x86_64/
	enabled=1

	sudo yum -y --releasever=7 --installroot=~/centos groupinstall "Base"

	sudo chroot centos
	passwd root

	sudo systemd-nspawn -b -D ~/centos

Create user to use with ansible as root
User name should be ansible

	yum install python openssh-server zsh bash-completion sudo
	useradd -m -G wheel -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	curl https://github.com/masasam.keys >> ~/.ssh/authorized_keys ← Register public key registered with github

Return to root

	systemctl enable sshd
	systemctl start sshd

Set host name

	hostname centos

vi /etc/hosts

	127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 centos

vi /etc/pam.d/su

	# Remove comment out
	auth required pam_wheel.so use_uid

Set up a user (group) that sudo can use

visudo

	#Defaults    requiretty(Confirm whether commented out)

	echo 'ansible ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) ALL' | sudo EDITOR='tee -a' visudo
	echo '%wheel ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo

Set the following in .ssh/config on your laptop or desktop

	Host centostest
						HostName localhost
						User ansible

Write at main.yml

	- hosts: centostest

Run playbook

	ansible-playbook main.yml
