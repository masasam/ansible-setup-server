## ansible でプロビジョニングしたいサーバーの準備

対象 OS  
Archlinux  
Debian8 stretch  
Centos7  

root で ansible で利用する user を作成  
user 名は ansible にする  

    useradd -m -G wheel -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	vi authorized_keys ← id_rsa.pub キーを登録

root に戻って  

	systemctl enable sshd
	systemctl start sshd

ホスト名を設定(archlinux とする)  

    hostname archlinux

vi /etc/hosts  

    127.0.0.1   localhost.localdomain   localhost archlinux

vi /etc/pam.d/su  

    # コメントアウトを外す
    auth required pam_wheel.so use_uid

visudo  

    #Defaults    requiretty(コメントアウトしてあるか確認)

    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    # Uncomment to allow members of group wheel to execute any command
    %wheel ALL=(ALL) ALL

    ## Same thing without a password
    %wheel ALL=(ALL) NOPASSWD: ALL

## 自分のマシンに ansible をインストール

    sudo pacman -S ansible
	ghq get -p masasam/ansible-vps

## プロビジョニングを実行

	ansible-playbook main.yml

group_vars/vps.yml に変数とパスワードを書いておく  
vps.yml はあらかじめ以下のコマンドで暗号化しておく  

	ansible-vault encrypt vps.yml

ansible.cfg に暗号のパスワードの場所を書いておくと毎回パスワードを打たなくていい  
(中身はパスワードだけ)  

	vault_password_file = ~/Dropbox/ansible/vault_pass

vps.yml の中身  

	hostname: 'yourhost' ← linux ホスト名
	domain: 'yourdomain' ← メインドメイン
	subdomain: 'subdomain.yourdomain' ← サブドメイン(blog に使う)
	username: 'ansible' ← ansible が ssh する user 名
	mailroot: 'youremailaddress' ← root のメールを転送するメールアドレス
	monitalert: 'youremailaddress' ← monit からのアラートメールの宛先
	infopassword: '913336a8ecba7764cd81245c2c6b'
	mariadbrootpassword: 'mariadbrootpassword' ← mariadb の root ユーザーのパスワード
	mackerelapikey: 'yourmackerelapikey' ← mackerel の apikey
	dbname: 'yourdbbame' ← mariadb で利用する DB 名
	dbpassword: 'yourdbpassword' ← そのパスワード
    docroot: '/home/html' ← メインドキュメントルート
    docrootblog: '/home/blog' ← blog のドキュメントルート
    docrootadminer: '/usr/share/webapps/adminer' ← adminer のドキュメントルート

infopassword は info@yourdomain のメールアドレスのパスワードになる  
infopassword の作り方  

    doveadm pw
	Enter new password: yourpassword
	Retype new password: yourpassword

と打つと

	{CRAM-MD5}913336a8ecba7764cd81245c2c6b

がでるので

	infopassword: '913336a8ecba7764cd81245c2c6b'

とする

#### サーバーのアップデートだけする playbook

    ansible-playbook update.yml

## テスト用ゲストコンテナをローカルに作る

---- テスト環境が不要なら以下は必要ない ----

ゲスト環境は本番環境の vps と  
ゲストテスト環境の systemd-nspawn  
以下 systemd-nspawn は vps では ssh で読み替えて構築する  

テスト用コンテナを用意

	sudo pacman -S arch-install-scripts
	mkdir systemdcontainer
	sudo pacstrap -i -c -d ~/systemdcontainer base base-devel --ignore linux
    sudo systemd-nspawn -b -D ~/systemdcontainer --bind=/var/cache/pacman/pkg

コンテナ内で  

	pacman -Sy bash-completion openssh

arch linux は python3 がデフォルトなので  
ansible が python2 を使えるようにする  
(centos8 も python3 になるようなので気をつける)  

	pacman -Sy python2 zsh

ansible で利用する user を作成  

    useradd -m -G wheel -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	vi authorized_keys ← id_rsa.pub キーを登録

root に戻って  

	systemctl enable sshd
	systemctl start sshd

ホスト名を設定

    hostname archtest

vi /etc/hosts

    127.0.0.1   localhost.localdomain   localhost archtest

#### root になれるユーザを wheel グループに属するユーザのみにする

    usermod -G wheel ansible

vi /etc/pam.d/su  

    # コメントアウトを外す
    auth required pam_wheel.so use_uid

#### sudo が使えるユーザ（グループ）を設定する

visudo  

    #Defaults    requiretty(centos の場合のみコメントアウトしておく)

    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    # Uncomment to allow members of group wheel to execute any command
    %wheel ALL=(ALL) ALL

    ## Same thing without a password
    %wheel ALL=(ALL) NOPASSWD: ALL

>Ctrl-]]]
でシャットダウン

ssh でつながるようになったから次回以降はバックグラウンドで起動してよい。  
(ssh でログインしてシャットダウンできるようになったため)  

    sudo systemd-nspawn -b -D ~/systemdcontainer --bind=/var/cache/pacman/pkg &

.ssh/config に以下を設定して

	Host archtest
                        HostName localhost
                        User ansible

ssh でコンテナにログイン

	ssh archtest

## debian のテスト用コンテナを作る場合

	sudo pacman debootstrap
	yaourt -S debian-archive-keyring

	mkdir debian
	sudo debootstrap stretch debian http://ftp.jaist.ac.jp/pub/Linux/debian/

	sudo chroot debian
	passwd root

	sudo systemd-nspawn -b -D ~/debian

ここから debian 仮想サーバー  

	apt-get install python openssh-server zsh bash-completion sudo

	useradd -m -G sudo -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	vi authorized_keys ← id_rsa.pub キーを登録

root に戻って  

	systemctl enable ssh
	systemctl start ssh

ホスト名を設定(debian とする)  

    hostname debian

vi /etc/hosts

    127.0.0.1       localhost debian

sudo が使えるユーザ（グループ）を設定する  

	update-alternatives --config editor

visudo  

    #Defaults    requiretty(コメントアウトしてあるか確認)

    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    # Uncomment to allow members of group wheel to execute any command
    %sudo ALL=(ALL) ALL

    ## Same thing without a password
    %sudo ALL=(ALL) NOPASSWD: ALL

## centos のテスト用コンテナを作る場合

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

root で ansible で利用する user を作成  
user 名は ansible にする  

	yum install python openssh-server zsh bash-completion sudo
    useradd -m -G wheel -s /bin/zsh ansible
	su - ansible
	ssh-keygen -t rsa -b 4096
	cd .ssh/
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys
	vi authorized_keys ← id_rsa.pub キーを登録

root に戻って  

	systemctl enable sshd
	systemctl start sshd

ホスト名を設定(archlinux とする)  

    hostname centos

vi /etc/hosts  

    127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 centos

vi /etc/pam.d/su  

    # コメントアウトを外す
    auth required pam_wheel.so use_uid

sudo が使えるユーザ（グループ）を設定する  

visudo  

    #Defaults    requiretty(コメントアウトしてあるか確認)

    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    # Uncomment to allow members of group wheel to execute any command
    %wheel ALL=(ALL) ALL

    ## Same thing without a password
    %wheel ALL=(ALL) NOPASSWD: ALL
