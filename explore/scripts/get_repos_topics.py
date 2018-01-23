import helpers
import json
import re

datfilepath = "../github-data/labRepos_Topics.json"
allData = {}

# Read repo info data file (to use as repo list)
dataObj = helpers.read_json("../github-data/labReposInfo.json")

# Populate repo list
repolist = []
print("Getting internal repos ...")
repolist = sorted(dataObj["data"].keys())
print("Repo list complete. Found %d repos." % (len(repolist)))

# Read pretty GraphQL query
query_in = helpers.read_gql("../queries/repo-Topics.gql")

# Retrieve authorization token
authhead = helpers.get_gitauth()

# Iterate through internal repos
print("Gathering data across multiple paginated queries...")
collective = {u'data': {}}
tab = "    "

for repo in repolist:
	pageNum = 1
	print("\n'%s'" % (repo))
	print(tab + "page " + str(pageNum))

	repoSplit = repo.split("/")

	print(tab + "Modifying query...")
	newqueryRep = re.sub('OWNNAME', repoSplit[0], query_in)
	newqueryRep = re.sub('REPONAME', repoSplit[1], newqueryRep)
	newquery = re.sub(' PGCURS', '', newqueryRep)
	gitquery = json.dumps({'query': newquery})
	print(tab + "Query ready!")

	# Actual query exchange
	outObj = helpers.query_github(authhead, gitquery)
	if outObj["errors"]:
		print(tab + "Could not complete '%s'" % (repo))
		collective["data"].pop(repo, None)
		continue
	# Update collective data
	collective["data"][repo] = outObj["data"]["repository"]

	# Paginate if needed
	hasNext = outObj["data"]["repository"]["repositoryTopics"]["pageInfo"]["hasNextPage"]
	while hasNext:
		pageNum += 1
		print(tab + "page %d" % (pageNum))
		cursor = outObj["data"]["repository"]["repositoryTopics"]["pageInfo"]["endCursor"]

		print(tab + "Modifying query...")
		newquery = re.sub(' PGCURS', ', after:"' + cursor + '"', newqueryRep)
		gitquery = json.dumps({'query': newquery})
		print(tab + "Query ready!")

		# Actual query exchange
		outObj = helpers.query_github(authhead, gitquery)
		if outObj["errors"]:
			print(tab + "Could not complete '%s'" % (repo))
			collective["data"].pop(repo, None)
			continue

		# Update collective data
		collective["data"][repo]["repositoryTopics"]["nodes"].extend(outObj["data"]["repository"]["repositoryTopics"]["nodes"])
		hasNext = outObj["data"]["repository"]["repositoryTopics"]["pageInfo"]["hasNextPage"]

	del collective["data"][repo]["repositoryTopics"]["pageInfo"]
	print("'%s' Done!" % (repo))

print("\nCollective data gathering complete!")

# Combine new data with existing data
allData["data"] = collective["data"]
allDataString = json.dumps(allData, indent=4, sort_keys=True)

# Write output file
print("\nWriting file '%s'" % (datfilepath))
with open(datfilepath, "w") as fileout:
	fileout.write(allDataString)
print("Wrote file!")

print("\nDone!\n")
