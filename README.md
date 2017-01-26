## 自分のマシンに ansible をインストール

    sudo pacman -S ansible
	ghq get -p masasam/ansible-vps

## ansible でプロビジョニングしたいサーバーを準備

centos 対応はすぐできるので対象サーバーを archlinux とした  
(自分サーバーが archlinux で構築してるからというくだらない理由)  

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

root になれるユーザを wheel グループに属するユーザのみにする  

    usermod -G wheel ansible

vi /etc/pam.d/su  

    # コメントアウトを外す
    auth required pam_wheel.so use_uid

sudo が使えるユーザ（グループ）を設定する  

visudo  

    #Defaults    requiretty(コメントアウトしてあるか確認)

    #ansible に sudo 権限を与えておく
    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    ##wheel グループに sudo 権限を与える
    # Uncomment to allow members of group wheel to execute any command
    %wheel ALL=(ALL) ALL

    ##ansible だけはパスワード無で sudo できるようにする
    #(正確には wheel グループに与えるのでむやみに wheel グループに user をいれないように)
    ## Same thing without a password
    %wheel ALL=(ALL) NOPASSWD: ALL

## プロビジョニングを実行

	ansible-playbook main.yml --extra-vars "@private.yml"

private.yml に変数とパスワードを書いておく  
private.yml はあらかじめ以下のコマンドで暗号化しておく  

	ansible-vault encrypt private.yml

ansible.cfg に暗号のパスワードの場所を書いておくと毎回パスワードを打たなくていい  
(中身はパスワードだけ)  

	vault_password_file = ~/Dropbox/ansible/vault_pass

private.yml の中身  

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

    ansible-playbook update.yml --extra-vars "@private.yml"

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

ゲストも Arch Linux なので  

	pacman -Sy bash-completion openssh

arch linux は python3 がデフォルトなので  
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

    #ansible に sudo 権限を与えておく(su できなくなったときの保険のため)
    ## User privilege specification
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    ##wheel グループに sudo 権限を与える
    # Uncomment to allow members of group wheel to execute any command
    %wheel ALL=(ALL) ALL

    ##ansible だけはパスワード無で sudo できるようにする
    #(正確には wheel グループに与えるのでむやみに wheel グループに user をいれないように)
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
