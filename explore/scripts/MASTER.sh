# Run this script to refresh all data for today


# On exit
function finish {
	# Log end time
	echo "End" >> ../github-data/LAST_MASTER_UPDATE.txt
	date >> ../github-data/LAST_MASTER_UPDATE.txt
}
trap finish EXIT

# Stop and Log for failed scripts
function errorCheck() {
	if [ $ret -ne 0 ]; then
		echo "FAILED - $1"
		echo "FAILED - $1" >> ../github-data/LAST_MASTER_UPDATE.txt
		exit
	fi
}

# Basic script run procedure
function runScript() {
	echo "Run - $1"
	python $1
	ret=$?
	errorCheck "$1"
}


echo "RUNNING MASTER UPDATE SCRIPT"

# Log start time
date '+%Y-%m-%d' > ../github-data/LAST_MASTER_UPDATE.txt
echo "Start" >> ../github-data/LAST_MASTER_UPDATE.txt
date >> ../github-data/LAST_MASTER_UPDATE.txt


# RUN THIS FIRST
runScript cleanup_inputs.py


# --- BASIC DATA ---
# Required before any other repo scripts (output used as repo list)
runScript get_repos_info.py
# Required before any other member scripts (output used as member list)
runScript get_llnl_members.py


# --- EXTERNAL V INTERNAL ---
runScript get_members_extrepos.py
runScript get_repos_extusers.py


# --- ADDITIONAL REPO DETAILS ---
runScript get_repos_licenses.py
runScript get_repos_languages.py
runScript get_repos_topics.py
runScript get_repos_pullsissues.py
runScript get_repos_activity.py


# --- HISTORY FOR ALL TIME ---
runScript get_repos_creationhistory.py

# RUN THIS LAST, used in case of long term cumulative data
runScript build_yearlist.py


echo "MASTER UPDATE COMPLETE"
