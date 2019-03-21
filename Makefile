all:	setup
	cd ./maszyna_rejestrowa && make


setup:
	./setup.sh


clean:
	-rm parser.out parsetab.py __pycache__ -rf
	-cd ./maszyna_rejestrowa && make cleanall
