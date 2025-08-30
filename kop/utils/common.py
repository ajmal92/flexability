def get_user_branch(user):
    """
    Get the branch associated with a user, whether they're a doctor or branch admin.
    Returns None if user doesn't have either profile.
    """
    if hasattr(user, 'doctor_profile'):
        return user.doctor_profile.branch
    elif hasattr(user, 'branch_admin'):
        return user.branch_admin.branch
    return None
