svg: 
	( \
		source ./env/bin/activate; \
		pyreverse -o png -p MyCapytain MyCapytain; \
		pyreverse -o svg -p MyCapytain MyCapytain; \
	)