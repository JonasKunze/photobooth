install-dependencies:
	apt-get install daemontools daemontools-run

install: install-dependencies
	ln -s `pwd`/service/ /etc/service/photobooth

uninstall:
	rm /etc/service/photobooth

start:
	python main.py

start-service:
	svc -u service

stop-service:
	svc -d service
	pkill photobooth
