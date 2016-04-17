ANSIBLE := $(shell ansible --version)
VAGRANT := $(shell vagrant --version)

all: load deploy run

ansible:
ifndef ANSIBLE
	@echo -e "\033[0;31mAnsible was not detected, attempting to install via pip...\033[0m"
	pip install ansible && echo -e "\033[1;34mAnsible is now installed.\033[0m" || echo -e "\033[0;31ERROR: Failed to install Ansible, please install using your system's package manager.\033[0m"
endif

vagrant:
ifndef VAGRANT
	@echo -e "\033[0;31Vagrant was not detected, please install via your system's package manager...\033[0m"
	exit 1
endif

provision: ansible
	@echo -e "\033[1;34mBringing up PSQL virtual machine...\033[0m"
	vagrant up --provision
	@echo -e "\033[0;32mProvisioning successful!\033[0m"

download:
	@echo -e "\033[1;34mDownloading source files...\033[0m"
	if [ ! -f data/ccdb.csv ]; then curl -o data/ccdb.csv "https://data.consumerfinance.gov/views/s6ew-h6mp/rows.csv"; fi;
	if [ ! -f data/20135us0015000.zip ]; then curl -o data/20135us0015000.zip "http://www2.census.gov/acs2013_5yr/summaryfile/2009-2013_ACSSF_By_State_By_Sequence_Table_Subset/UnitedStates/All_Geographies_Not_Tracts_Block_Groups/20135us0015000.zip"; fi;
	if [ ! -f data/g20135us.csv ]; then curl -o data/g20135us.csv "http://www2.census.gov/acs2013_5yr/summaryfile/2009-2013_ACSSF_By_State_By_Sequence_Table_Subset/UnitedStates/All_Geographies_Not_Tracts_Block_Groups/g20135us.csv"; fi;
	@echo -e "\033[0;32mDownloading has completed.\033[0m"

extract: download
	@echo -e "\033[1;34mExtracting compressed data...\033[0m"
	unzip -o data/20135us0015000.zip -d data
	@echo -e "\033[0;32mExtraction has completed.\033[0m"

transform: extract
	@echo -e "\033[1;34mTransforming data in preparation for load...\033[0m"
	sed -i -- 's/\.//g' data/e20135us0015000.txt
	sed -i -- 's/\.//g' data/m20135us0015000.txt
	@echo -e "\033[0;32mTransform has completed.\033[0m"

load: provision transform
	@echo -e "\033[1;34mLoading data into PSQL...\033[0m"
	vagrant ssh -c "psql -U postgres < /vagrant/sql_scripts/ddl.sql"
	vagrant ssh -c "psql -U postgres -c \"TRUNCATE e20135us0015000; COPY e20135us0015000 FROM '/vagrant/data/e20135us0015000.txt' DELIMITER ',' CSV\""
	vagrant ssh -c "psql -U postgres -c \"TRUNCATE m20135us0015000; COPY m20135us0015000 FROM '/vagrant/data/m20135us0015000.txt' DELIMITER ',' CSV\""
	vagrant ssh -c "psql -U postgres -c \"SET CLIENT_ENCODING TO 'ISO_8859_8'; TRUNCATE g20135us; COPY g20135us FROM '/vagrant/data/g20135us.csv' DELIMITER ',' CSV\""
	vagrant ssh -c "psql -U postgres -c \"TRUNCATE ccdb; COPY ccdb (date_received, product, sub_product, issue, sub_issue, narrative, company_response_public, company, state, zip_code, tags, consumer_consent_provided, submitted_via, date_sent_to_company, company_response_consumer, timely_response, consumer_disputed, complaint_id) FROM '/vagrant/data/ccdb.csv' DELIMITER ',' HEADER CSV\""
	@echo -e "\033[0;32mData loading was successful!\033[0m"

deploy: provision
	@echo -e "\033[1;34mDeploying Python application...\033[0m"
	vagrant ssh -c "virtualenv ~/.virtualenvs/ccdb_viz"
	vagrant ssh -c "~/.virtualenvs/ccdb_viz/bin/pip install -r /vagrant/ccdb_viz/requirements.txt"

run:
	@echo -e "\033[1;34mRunning application server...\033[0m"
	vagrant ssh -c "cd /vagrant/ccdb_viz && ~/.virtualenvs/ccdb_viz/bin/bokeh serve --show main.py --address=0.0.0.0 --host=192.168.56.2:5006"
	@echo -e "\033[0;32mDemo completed! I hope you enjoyed it.\033[0m"
