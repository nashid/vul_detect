from git import Repo,Git

def checkout_to(repo_dir,commit_id,past_branch_name):
    """
    @description  :
    switch current workspace to commit workspace
    @param  :
    repo_dir:
    commit_id:
    @Returns  :
    repo:
    """
    print('checkout workspace to {} from {}'.format(commit_id, past_branch_name))
    repo = Repo(repo_dir)
    r = Git(repo_dir)
    past_branch_name = past_branch_name
    repo.create_head(past_branch_name ,commit_id)
    try:
        r.execute('git checkout '+past_branch_name+' -f', shell=True)
    except:
        r.execute('git branch -D '+past_branch_name, shell=True)
        r.execute('git checkout '+past_branch_name+' -f', shell=True)
    print('checkout end !')
    
    return r


def checkout_back(r, past_branch_name):
    """
    @description  :
    ---------back to current workspace
    @param  :
    -------
    @Returns  :
    -------
    """
    print('checkout workspace to current')
    try:
        r.execute('git checkout master -f', shell=True)
    except:
        r.execute('git checkout unstable -f', shell=True)
    r.execute('git branch -D '+past_branch_name, shell=True)
    print('checkout end !')
    