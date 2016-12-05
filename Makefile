svg: 
	( \
		source ./env/bin/activate; \
		pyreverse -o png -p MyCapytain MyCapytain; \
		pyreverse -o svg -p MyCapytain MyCapytain; \
		pyreverse -o svg -p MyCapytain -c MyCapytain.resolvers.cts.api.HttpCTSResolver MyCapytain; \
		pyreverse -o svg -p MyCapytain -c MyCapytain.resources.texts.api.cts.Text MyCapytain; \
		pyreverse -o svg -p MyCapytain -c MyCapytain.resources.texts.api.cts.Passage MyCapytain; \
	)