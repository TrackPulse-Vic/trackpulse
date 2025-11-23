import requests


def getTrainImage(number, thumbnail=False):
    apiURL = f"https://victorianrailphotos.com/api/photos/{number}"
    
    if thumbnail:
        thummy = 'thumbnail'
    else:
        thummy = 'url'
    
    # Make a GET request to fetch the photo data
    try:
        response = requests.get(apiURL)
        if response.status_code != 200:
            return None, None
        
        photos = response.json().get('photos', [])
        featured_photos = [photo for photo in photos if photo.get('featured') == 1]
        
        if featured_photos:
            photo = featured_photos[-1]
            photo_url = photo[f'{thummy}']
            photographer = photo.get('photographer', 'Unknown')
            url_response = requests.head(photo_url)
            if url_response.status_code == 200:
                try:
                    response = requests.get(f'https://victorianrailphotos.com/api/view/{photo["id"]}/train')
                    print('added view count api')
                    print('response: ', response.text)
                except Exception as e:
                    print('couldnt add view count api')
                    print('error: ', e)
                return photo_url, photographer
            return None, None
        
        if photos:
            photo = photos[-1]
            photo_url = photo[f'{thummy}']
            photographer = photo.get('photographer', 'Unknown')
            url_response = requests.head(photo_url)
            if url_response.status_code == 200:
                try:
                    requests.get(f'https://victorianrailphotos.com/api/view/{photo["id"]}/train')
                    print('added view count api')
                    print('response: ', response.text)
                except Exception as e:
                    print('couldnt add view count api')
                    print('error: ', e)
                return photo_url, photographer
            return None, None
        
        return None, None
    
    except requests.RequestException:
        return None, None