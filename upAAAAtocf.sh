#!/usr/bin/env bash
#!/bin/sh
# 使用方法 ./upAAAAtocf.sh 二级域名
cloudflare_Email='lvusyy@qq.com'
cloudflare_Key='xxxxxxxxxxxxxxxx'
cloudflare_domian='showip.xyz'
cloudflare_host=''
cloudflare_domian2=''
cloudflare_host2=''
cloudflare_domian6=$1
cloudflare_host6=`ifconfig eth0 | awk '/inet6/{print $2}' | grep -v "fe80"`
cloudflare_interval=10

IPv6=1
domain_type="AAAA"
hostIP=$cloudflare_host6
Zone_ID=""
DOMAIN=$cloudflare_domian
HOST=$1


Zone_ID=""
get_Zone_ID() {
# 获得Zone_ID
Zone_ID=$(curl -L -k -s -X GET "https://api.cloudflare.com/client/v4/zones" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json")
Zone_ID=$(echo $Zone_ID|grep -o "id\":\"[0-9a-z]*\",\"name\":\"$DOMAIN\",\"status\""|grep -o "id\":\"[0-9a-z]*\""| awk -F : '{print $2}'|grep -o "[a-z0-9]*")

}

arDdnsInfo() {
if [ "$IPv6" = "1" ]; then
	domain_type="AAAA"
else
	domain_type="A"
fi

case  $HOST  in
	  \*)
		host_domian="\\$HOST.$DOMAIN"
		;;
	  \@)
		host_domian="$DOMAIN"
		;;
	  *)
		host_domian="$HOST.$DOMAIN"
		;;
esac

# 获得Zone_ID
echo `get_Zone_ID`
# 获得最后更新IP
recordIP=$(curl -L -k -s -X GET "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json")
RECORD_ID=$(echo $recordIP | sed -e "s/"'"ttl":'"/"' \n '"/g" | grep "type\":\"$domain_type\"" | grep -o "id\":\"[0-9a-z]\{32,\}\",\"type\":\"[^\"]*\",\"name\":\"$host_domian\",\"content\":\""|grep -o "id\":\"[0-9a-z]\{32,\}\",\""| awk -F : '{print $2}'|grep -o "[a-z0-9]*")
recordIP=$(echo $recordIP | sed -e "s/"'"ttl":'"/"' \n '"/g" | grep "type\":\"$domain_type\"" | grep -o "name\":\"$host_domian\",\"content\":\"[^\"]*\""| awk -F 'content":"' '{print $2}' | tr -d '"' |head -n1)
# 检查是否有名称重复的子域名
if [ "$(echo $RECORD_ID | grep -o "[0-9a-z]\{32,\}"| wc -l)" -gt "1" ] ; then
	logger -t "【cloudflare动态域名】" "$HOST.$DOMAIN 获得最后更新IP时发现重复的子域名！"
	for Delete_RECORD_ID in $RECORD_ID
	do
	logger -t "【cloudflare动态域名】" "$HOST.$DOMAIN 删除名称重复的子域名！ID: $Delete_RECORD_ID"
	RESULT=$(curl -L -k -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records/$Delete_RECORD_ID" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json")
	done
	recordIP="0"
	echo $recordIP
	return 0
fi
	if [ "$IPv6" = "1" ]; then
	echo $recordIP
	return 0
	else
	case "$recordIP" in
	[1-9]*)
		echo $recordIP
		return 0
		;;
	*)
		echo "Get Record Info Failed!"
		#logger -t "【cloudflare动态域名】" "获取记录信息失败！"
		return 1
		;;
	esac
	fi

}



arNslookup6() {
mkdir -p /tmp/arNslookup
nslookup $1 | tail -n +3 | grep "Address" | awk '{print $3}'| grep ":" | sed -n '1p' > /tmp/arNslookup/$$ &
I=5
while [ ! -s /tmp/arNslookup/$$ ] ; do
		I=$(($I - 1))
		[ $I -lt 0 ] && break
		sleep 1
done
killall nslookup
if [ -s /tmp/arNslookup/$$ ] ; then
	cat /tmp/arNslookup/$$ | sort -u | grep -v "^$"
	rm -f /tmp/arNslookup/$$
fi
}

# 更新记录信息
# 参数: 主域名 子域名
arDdnsUpdate() {
I=3
RECORD_ID=""
if [ "$IPv6" = "1" ]; then
	domain_type="AAAA"
else
	domain_type="A"
fi

case  $HOST  in
	  \*)
		host_domian="\\$HOST.$DOMAIN"
		;;
	  \@)
		host_domian="$DOMAIN"
		;;
	  *)
		host_domian="$HOST.$DOMAIN"
		;;
esac

while [ "$RECORD_ID" = "" ] ; do
	I=$(($I - 1))
	[ $I -lt 0 ] && break
# 获得Zone_ID
get_Zone_ID
# 获得记录ID
RECORD_ID=$(curl -L -k -s -X GET "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json")
RECORD_ID=$(echo $RECORD_ID | sed -e "s/"'"ttl":'"/"' \n '"/g" | grep "type\":\"$domain_type\"" | grep -o "id\":\"[0-9a-z]\{32,\}\",\"type\":\"[^\"]*\",\"name\":\"$host_domian\",\"content\":\""|grep -o "id\":\"[0-9a-z]\{32,\}\",\""| awk -F : '{print $2}'|grep -o "[a-z0-9]*")
# 检查是否有名称重复的子域名
if [ "$(echo $RECORD_ID | grep -o "[0-9a-z]\{32,\}"| wc -l)" -gt "1" ] ; then
	logger -t "【cloudflare动态域名】" "$HOST.$DOMAIN 更新记录信息时发现重复的子域名！"
	for Delete_RECORD_ID in $RECORD_ID
	do
	logger -t "【cloudflare动态域名】" "$HOST.$DOMAIN 删除名称重复的子域名！ID: $Delete_RECORD_ID"
	RESULT=$(curl -L -k -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records/$Delete_RECORD_ID" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json")
	done
	RECORD_ID=""
fi
#echo "RECORD ID: $RECORD_ID"
sleep 1
done
if [ "$RECORD_ID" = "" ] ; then
	# 添加子域名记录IP
	RESULT=$(curl -L -k -s -X POST "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json" \
     --data '{"type":"'$domain_type'","name":"'$HOST'","content":"'$hostIP'","ttl":120,"proxied":false}')
	RESULT=$(echo $RESULT | grep -o "success\":[a-z]*,"|awk -F : '{print $2}'|grep -o "[a-z]*")
	echo "创建dns_records: $RESULT"
else
	# 更新记录IP
	RESULT=$(curl -L -k -s -X PUT "https://api.cloudflare.com/client/v4/zones/$Zone_ID/dns_records/$RECORD_ID" \
     -H "X-Auth-Email: $cloudflare_Email" \
     -H "X-Auth-Key: $cloudflare_Key" \
     -H "Content-Type: application/json" \
     --data '{"type":"'$domain_type'","name":"'$HOST'","content":"'$hostIP'","ttl":120,"proxied":false}')
	RESULT=$(echo $RESULT | grep -o "success\":[a-z]*,"|awk -F : '{print $2}'|grep -o "[a-z]*")
	echo "更新dns_records: $RESULT"
fi
if [ "$(printf "%s" "$RESULT"|grep -c -o "true")" = 1 ];then
	echo "$(date) -- Update success"
	return 0
else
	echo "$(date) -- Update failed"
	return 1
fi

}

arDdnsUpdate
