[[_TOC_]]

## Commit Messages for PRs

The final PR that you make to merge into main should have one commit per major feature. Ideally, each PR only includes one major feature. 

For example, a PR to include a new S3 file upload utility method would have the commit:

```
1234: Add S3 file upload utility in S3FileUploader class.
```

Where 1234 is the ticket number associated with the feature.

## Commit Messages During Development

In reality, the actual development process may include many commits, not just one final clean commit. For the example above, there may have been many commits that were made along the way:

```
Add initial file & stub
---
Flesh out stub, initial testing
---
Changes based on e2e testing
---
Integrate uploader into existing classes
--- 
Feedback from review
```

The thing that matters is that the **_final commit in a PR_** is clean. We do this by **rebasing and squashing commits**.

## Rebasing and Squashing Commits

A [rebase](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase#:~:text=Rebase%20is%20one%20of%20two,has%20powerful%20history%20rewriting%20features.) is a method to update your current branch with the commits that have been made in an upstream branch.

Essentially, this process removes all of your commits, pulls from the upstream branch, and then applies all of your commits back on top of the updated repo. This is a cleaner method of updating your code than [merging](https://stackoverflow.com/questions/804115/when-do-you-use-git-rebase-instead-of-git-merge). Merging is appropriate for integrating our code into the main branch, but rebasing is preferred to update our branch with unrelated code from other developers.

During a rebase, you have the option to rewrite your commit history. This means that we can interactively squash all of our commits into one clean, final commit, when we're ready to make a PR.

For the example above, the git process would look something like this:

```bash
$ git checkout main
$ git pull
$ git branch feature/1234-add-s3-uploader
$ git checkout feature/1234-add-s3-uploader
$ ... Develop features ...
$ git commit {files} -m "Add initial file & stub"
$ ... Develop features ...
$ git commit {files} -m "Flesh out stub, initial testing"
$ ... Develop features ...
$ git commit {files} -m "Changes based on e2e testing"
$ ... Develop features ...
$ git commit {files} -m "Integrate uploader into existing classes"
$ ... Develop features ...
$ git commit {files} -m "Feedback from review"
$ ... Ready for PR. 
  ... But, other developers may have made changes to main in the meantime,
  ... and our commit history is messy. Need to change our commit history, and
  ... update with the latest code on main to check for conflicts ...
$ git fetch
$ git rebase origin/main --interactive
 ... inside of the editor (e.g. vim) you will see:
 # pick {sha} Add initial file & stub
 # pick {sha} Flesh out stub, initial testing
 # pick {sha} Changes based on e2e testing
 # pick {sha} Integrate uploader into existing classes
 # pick {sha} Feedback from review

We can then change this to squash our commits:

 # pick {sha} Add initial file & stub
 # squash {sha} Flesh out stub, initial testing
 # squash {sha} Changes based on e2e testing
 # squash {sha} Integrate uploader into existing classes
 # squash {sha} Feedback from review

Which will allow us to reword our commit messages to just be:

1234: Add S3 file upload utility in S3FileUploader class.

$ ... It is possible we find conflicts between main and our branch - if so, need to handle conflicts manually
  ... and after saving the files, mark the conflict resolved:
  git add {conflicted file}
  git rebase --continue
  ... otherwise we are done

... Need to force push since we rewrote our old commit history:
$ git push --force
 ```
