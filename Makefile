create_docs:
	@echo ">>> CREATE DOCS"
	@jupyter nbconvert --to markdown ./2018-2019/Fantastats1819.ipynb --no-input --output-dir ./website/docs
	@jupyter nbconvert --to markdown ./2019-2020/Fantastats1920.ipynb --no-input --output-dir ./website/docs
	@jupyter nbconvert --to markdown ./2020-2021/Fantastats2021.ipynb --no-input --output-dir ./website/docs
	@jupyter nbconvert --to markdown ./2021-2022/Fantastats2122.ipynb --no-input --output-dir ./website/docs
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

