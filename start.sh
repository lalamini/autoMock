#docker run -d --name uiMock_bridge -v `pwd`/app:/home/docker/code/app -v `pwd`/log:/var/log/supervisor -e RUNMODE=bridge  -p 8010:80 webapp:1.4_common
docker run -d --name uiMock_proxy -v `pwd`/app:/home/docker/code/app -v `pwd`/log:/var/log/supervisor -e RUNMODE=proxy  -p 8010:80 webapp:1.4_common


