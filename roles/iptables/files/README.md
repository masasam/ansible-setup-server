# iptables のベースを作る

空にして作業開始

    iptables-restore < /etc/iptables/empty.rules

iptables コマンドを叩いてルールを作っていく

	iptables -N TCP
	iptables -N UDP
	iptables -P FORWARD DROP
	iptables -P OUTPUT ACCEPT
	iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	iptables -P INPUT DROP
	iptables -A INPUT -i lo -j ACCEPT
	iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
	iptables -A INPUT -p icmp --icmp-type 8 -m conntrack --ctstate NEW -j ACCEPT
	iptables -A INPUT -p udp -m conntrack --ctstate NEW -j UDP
	iptables -A INPUT -p tcp --syn -m conntrack --ctstate NEW -j TCP
	iptables -A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
	iptables -A INPUT -p tcp -j REJECT --reject-with tcp-reset
	iptables -A INPUT -j REJECT --reject-with icmp-proto-unreachable
	iptables -A TCP -p tcp --dport 22 -j ACCEPT
	iptables -A TCP -p tcp --dport 80 -j ACCEPT
	iptables -A TCP -p tcp --dport 443 -j ACCEPT
	iptables -A UDP -p udp --dport 53 -j ACCEPT
	iptables -A TCP -p tcp --dport 25 -j ACCEPT
	iptables -A TCP -p tcp --dport 465 -j ACCEPT
	iptables -A TCP -p tcp --dport 110 -j ACCEPT
	iptables -A TCP -p tcp --dport 995 -j ACCEPT
	iptables -A TCP -p tcp --dport 143 -j ACCEPT
	iptables -A TCP -p tcp --dport 993 -j ACCEPT
	iptables -A TCP -p tcp --dport 587 -j ACCEPT
	iptables -I TCP -p tcp -m recent --update --seconds 60 --name TCP-PORTSCAN -j REJECT --reject-with tcp-reset
	iptables -D INPUT -p tcp -j REJECT --reject-with tcp-reset
	iptables -A INPUT -p tcp -m recent --set --name TCP-PORTSCAN -j REJECT --reject-with tcp-reset
	iptables -I UDP -p udp -m recent --update --seconds 60 --name UDP-PORTSCAN -j REJECT --reject-with icmp-port-unreachable
	iptables -D INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
	iptables -A INPUT -p udp -m recent --set --name UDP-PORTSCAN -j REJECT --reject-with icmp-port-unreachable

これらの設定を保存して/etc/iptables/iptables.rules を得る

	iptables-save > /etc/iptables/iptables.rules

iptables.rules を files フォルダに入れて ansible でプロビジョニングする
