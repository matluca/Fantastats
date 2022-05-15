files := ./2018-2019/Fantastats1819.ipynb ./2019-2020/Fantastats1920.ipynb ./2020-2021/Fantastats2021.ipynb ./2021-2022/Fantastats2122.ipynb

create_docs:
	@echo ">>> CREATE DOCS"
	@$(foreach file, $(files),\
		jupyter nbconvert --to markdown $(file) \
		--RegexRemovePreprocessor.patterns="%%writefile.*" \
		--RegexRemovePreprocessor.patterns="###.*\s\|\s.*" \
		--RegexRemovePreprocessor.patterns="#\sScores\stxt\sfiles" \
		--no-input --output-dir ./website/docs;)
	@jupyter nbconvert --to markdown All-Time-Luck.ipynb --no-input --output-dir ./website/docs

build_site:
	@echo ">>> BUILD SITE"
	@cd website && mkdocs build

site: create_docs build_site

test_site:
	@echo ">>> TEST SITE"
	@firebase serve

deploy:
	@echo ">>> DEPLOY SITE"
	@firebase deploy

