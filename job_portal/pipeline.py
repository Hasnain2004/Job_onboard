from django.contrib import messages

def save_profile(backend, user, response, *args, **kwargs):
    """
    Custom pipeline function to save Google profile data to our User model
    """
    if backend.name == 'google-oauth2':
        if response.get('name'):
            user.full_name = response.get('name')
        
        # If email not already set and available in response
        if not user.email and response.get('email'):
            user.email = response.get('email')
        
        # Set default role if needed
        if not user.role:
            user.role = 'jobseeker'
            
        # Add profile picture if available
        if response.get('picture'):
            # Check if the model has either of these attributes before setting
            if hasattr(user, 'profile_pic_url'):
                user.profile_pic_url = response.get('picture')
            elif hasattr(user, 'profile_image'):
                user.profile_image = response.get('picture')
        
        # Save the user object with updated info
        user.save()
    
    return {
        'user': user,
        'is_new': kwargs.get('is_new', False)
    } 