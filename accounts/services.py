def update_profile_image(user, image):
    user.profile_image = image
    user.save(update_fields=["profile_image"])
    return user