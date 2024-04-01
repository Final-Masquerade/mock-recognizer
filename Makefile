start: clean
	python src/app.py

output: clean
	python src/app.py --save-on-process

clean:
	rm -rf out temp