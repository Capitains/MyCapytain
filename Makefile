svg: 
	( \
		source ./env/bin/activate; \
		pyreverse -o png -p MyCapytain MyCapytain; \
		pyreverse -o svg -p MyCapytain MyCapytain; \
	)

classes:
	( \
		source ./env/bin/activate; \
		pyreverse -A -k -o svg -p MyCapytain_texts MyCapytain.resources.prototypes.text; \
		pyreverse -A -k -o png -p MyCapytain_texts MyCapytain.resources.prototypes.text;
	)

move:
	( \
		mv classes_* doc/_static/pyreverse/;\
		mv packages_* doc/_static/pyreverse/;\
	)

all:svg classes move