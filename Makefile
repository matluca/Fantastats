files := ./2018-2019/Fantastats1819.ipynb ./2019-2020/Fantastats1920.ipynb ./2020-2021/Fantastats2021.ipynb ./2021-2022/Fantastats2122.ipynb ./2022-2023/Fantastats2223.ipynb

define MANIFEST_LINK
<link rel="manifest" href="manifest.json">
endef

define SERVICE_WORKER
<script>\n  if (!navigator.serviceWorker.controller) {\n	  navigator.serviceWorker.register("\/sw.js").then(function(reg) {\n		  console.log("Service worker has been registered for scope: " + reg.scope);\n	  });\n  }\n<\/script>
endef

create_docs:
	@echo ">>> CREATE DOCS"
	@$(foreach file, $(files),\
		jupyter nbconvert --to markdown $(file) \
		--RegexRemovePreprocessor.patterns="%%writefile.*" \
		--RegexRemovePreprocessor.patterns="###.*\s\|\s.*" \
		--RegexRemovePreprocessor.patterns="##\sScores\stxt\sfiles" \
		--no-input --output-dir ./website/docs;)
	@jupyter nbconvert --to markdown All-Time-Luck.ipynb --no-input --output-dir ./website/docs

build_site:
	@echo ">>> BUILD SITE"
	@cd website && mkdocs build
	@cd website/site && sed -i '/^.*<\/head>.*/i ${MANIFEST_LINK}' index.html
	@cd website/site && sed -i '/^.*<\/body>.*/i ${SERVICE_WORKER}' index.html
	

site: create_docs build_site

test_site:
	@echo ">>> TEST SITE"
	@firebase serve

deploy:
	@echo ">>> DEPLOY SITE"
	@firebase deploy

