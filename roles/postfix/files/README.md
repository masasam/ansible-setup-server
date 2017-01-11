# postfix と dovecot で virtualmailuser

arch linux postfix パッケージは既に SASL のサポートを有効にしてコンパイルされているので、SASL 認証を使う場合、2 つの選択肢があります  
cyrus-sasl パッケージを使う。  
Dovecot を有効にして (Dovecot の認証だけでなく) Postfix の認証を処理させる。  

今回は cyrus-sasl なしのパターンで構築する  
STARTTLS POP3S で構築する  

## postfix

    sudo su -
    pacman -S postfix dovecot

vim /etc/postfix/main.cf  

    myhostname = archlinux

    mydomain = pansymade.net

    myorigin = $mydomain

    inet_interfaces = all

    mydestination = $myhostname, localhost.$mydomain, localhost

    mynetworks_style = host

    relayhost =

    home_mailbox = Maildir/

	inet_protocols = all

shell に戻って  

    groupadd -g 5000 vmail
    useradd -u 5000 -g vmail -s /usr/bin/nologin -d /home/vmail -m vmail

    cd /etc/ssl/private/
    openssl req -new -x509 -nodes -newkey rsa:4096 -keyout vmail.key -out vmail.crt -days 3650
    chmod 400 vmail.key
    chmod 444 vmail.crt

vim /etc/postfix/main.cf  

    smtpd_tls_security_level = may
    smtpd_tls_cert_file = /etc/letsencrypt/live/pansymade.net/fullchain.pem
    smtpd_tls_key_file = /etc/letsencrypt/live/pansymade.net/privkey.pem

vim /etc/postfix/master.cf  

    submission inet n       -       n       -       -       smtpd
     # SASL authentication with dovecot
      -o smtpd_sasl_auth_enable=yes
      -o smtpd_sasl_type=dovecot
      -o smtpd_sasl_path=private/auth
      -o smtpd_sasl_security_options=noanonymous
      -o smtpd_sasl_local_domain=$myhostname
      -o smtpd_client_restrictions=permit_sasl_authenticated,reject
      -o smtpd_recipient_restrictions=reject_non_fqdn_recipient,reject_unknown_recipient_domain,permit_sasl_authenticated,reject

vim /etc/postfix/main.cf  

    virtual_mailbox_domains = pansymade.net
    virtual_mailbox_base = /home/vmail
    virtual_mailbox_maps = hash:/etc/postfix/vmailbox
    virtual_uid_maps = static:5000
    virtual_gid_maps = static:5000
    virtual_alias_maps = hash:/etc/postfix/virtual

vim /etc/postfix/vmailbox   

    info@pansymade.net     pansymade.net/info/Maildir/

    postmap /etc/postfix/vmailbox
    postmap /etc/postfix/virtual

## dovecot

    cp /usr/share/doc/dovecot/example-config/dovecot.conf /etc/dovecot
    cp -r /usr/share/doc/dovecot/example-config/conf.d /etc/dovecot

vim /etc/dovecot/conf.d/10-auth.conf  

    auth_mechanisms = cram-md5 plain
    !include auth-passwdfile.conf.ext
    !include auth-static.conf.ext
    これ以外コメントアウト

vim /etc/dovecot/conf.d/auth-passwdfile.conf.ext  

    passdb {
        driver = passwd-file
        args = scheme=CRAM-MD5 username_format=%u /etc/dovecot/passwd
    }
    userdb {
        driver = passwd-file
        args = username_format=%u /etc/dovecot/passwd
    }
    これ以外コメントアウト

vim /etc/dovecot/conf.d/auth-static.conf.ext  

    userdb {
        driver = static
        args = uid=5000 gid=5000 home=/home/vmail/%d/%n
    }

    doveadm pw
Enter new password:
Retype new password:
{CRAM-MD5}913331d8782236a8ecba7764a63aa27b26437fd40ca878d887f11d81245c2c6b

vim /etc/dovecot/passwd にユーザーとパスワードを書き込み  

    info@pansymade.net:{CRAM-MD5}913331d8782236a8ecba7764a63aa27b26437fd40ca878d887f11d81245c2c6b
    改行を忘れないように

vim /etc/dovecot/conf.d/10-ssl.conf  

    ssl_cert = </etc/letsencrypt/live/pansymade.net/fullchain.pem
    ssl_key = </etc/letsencrypt/live/pansymade.net/privkey.pem

    mv /etc/postfix/aliases /etc/aliases
    root: masamasa@mailchodai.com
    newaliases

vim /etc/dovecot/dovecot.conf に追加  

    service auth {
      unix_listener /var/spool/postfix/private/auth {
        group = postfix
        mode = 0660
        user = postfix
      }
      user = root
    }


    systemctl restart postfix.service
    systemctl restart dovecot.service

    systemctl enable postfix.service
    systemctl enable Dovecot.service
