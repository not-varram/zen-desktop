#!/bin/bash
# read-only: show who/what closed each issue (timeline closed events + cross-referenced/merged PRs)
for n in "$@"; do
 echo "## $n"
 gh api repos/zen-browser/desktop/issues/$n/timeline --paginate --jq '.[]|select(.event=="closed" or .event=="marked_as_duplicate" or .event=="referenced" or (.event=="cross-referenced" and .source.issue.pull_request!=null))|[.event,(.actor.login//.source.issue.user.login),(.created_at//.source.issue.created_at),(.commit_id//""),(.source.issue.number//""|tostring),(.source.issue.title//""),(.source.issue.pull_request.merged_at//"")]|@tsv' 2>&1 | head -8
done
