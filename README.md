# ansible-vps
My vps server's ansible  

## ホスト側準備
---
ホストは Arch Linux なので  

    pacman -S ansible
	cd git
	git clone git@github.com:masasam/ansible-vps.git

## ゲスト側準備
---

ゲスト環境は本番環境の vps と  
ゲストテスト環境の systemd-nspawn  
以下 systemd-nspawn は vps では ssh で読み替えて構築する  

起動  

    sudo systemd-nspawn -b -D ~/systemdcontainer --bind=/var/cache/pacman/pkg

ゲストも Arch Linux なので  

	pacman -Sy bash-completion openssh
	
arch linux は python3 がデフォルトなので  
(centos8 も python3 になるようなので気をつける)  

	pacman -Sy python2

ansible で利用する user を作成  

    useradd -m -G wheel -s /bin/bash ansible
	su - ansible
	cd .ssh/
	ssh-keygen -t rsa -b 4096	
	mv id_rsa.pub authorized_keys
	chmod 600 authorized_keys

root に戻って  
	
	systemctl enable sshd
	systemctl start sshd

#### root になれるユーザを wheel グループに属するユーザのみにする

    usermod -G wheel ansible

vim /etc/pam.d/su  

    # コメントアウトを外す
    auth required pam_wheel.so use_uid


#### sudo が使えるユーザ（グループ）を設定する

export EDITOR=vim  
visudo  

    #Defaults    requiretty(centos の場合のみコメントアウトしておく)

    #ansible に sudo 権限を与えておく(su できなくなったときの保険のため)
    ## Allow root to run any commands anywhere
    root ALL=(ALL) ALL
    ansible ALL=(ALL) ALL

    ##wheel グループに sudo 権限を与える
    # Allows people in group wheel to run all commands
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

	Host archcontainer
                        HostName localhost
                        User ansible

ssh でコンテナにログイン

	ssh archcontainer
