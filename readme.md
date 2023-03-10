# Lingq to Anki Sync

## Primary Goals:
- Discover and document the lingq api, [their current documentation](https://www.lingq.com/apidocs/) does not list everything that is possible.
  - What is needed and not listed in their api docs:
    1. Update a lingq object (known status, srs due date)
    2. Get info on a specific lingq (not returning all)
- Come up with a system for equating anki card status(interval) with lingq known status (1,2,3,4,5).
- Import all words from lingq language to an anki deck.
- Sync anki status to lingq.
  - Need to figure out what status in anki should equate to what status in lingq.
  - set the lingq as reviewed if anki is reviewed.

## Future Goals:
- Import new cards from lingq to pre-existing deck.
- Import to custom deck.
- Sync with an already existing deck.
  - create new lingqs if the lingq doesn't exist yet.
  - update status if the word does exist.
- Allow user to define what interval relates to what lingq known status.
- Sync lingq status to anki


## Lingq API Documentation
### This is a temporary measure, hopefully lingq updates their own API docs, or I may make a better one than this. 

### Authentication
There is an API endpoint to retrieve your API key for lingq in their documentation. It's easiest to use this in dev at least. 

#### Api auth key is set up in postman as:
```
Type: API Key
Key: Authorization
value: Token {apiKey}
add to: Header
```


### Objects
#### Lingq object

Lingq object is refering to a single lingq (word).
```
{
    "pk": primaryKey,
    "url": url to get single card info,
    "term": string,
    "fragment": string,
    "importance": int,
    "status": int,
    "extended_status": null,
    "last_reviewed_correct": null,
    "srs_due_date": date,
    "notes": string,
    "audio": null,
    "words": string[],
    "tags": string[],
    "hints": hintObject[],
    "transliteration": {},
    "gTags": [],
    "wordTags": [],
    "readings": {}
}
```
#### Hint object
```
{
    "id": int,
    "locale": string,
    "text": string,
    "term": string,
    "popularity": int,
    "is_google_translate": bool,
    "flagged": bool
}
```


### GET
#### 1. Get lingqs from a language: 
`https://www.lingq.com/api/v3/{languageCode}/cards`

Will return this json with the first 100 lingqs:
```
{
    "count": int,
    "next": string,
    "previous": string,
    "results": [
        List of lingq objects
    ]
}
```

Add ?page={pageNumber} to return a specific page of cards

#### 2. Get single card by primary key
`https://www.lingq.com/api/v3/{languageCode}/cards/{primaryKey}/`

Will return a single lingq object that matches the primaryKey within the language code. If an invalid primaryKey is supplied the api will return a 404 Not found with a return body of 

```"detail": "Not Found."```


### Patch
#### 1. Update a lingq object
`https://www.lingq.com/api/v2/{languageCode}/cards/{primarykey}/`

Body Json object of the items that will be changing in the lingq object. 
Example:
```
{
    "status": 2
}
```
Note: Not all fields of the object can be updated here. I have tested the following:
1. status (the known status, 0-5).
2. tags

### Post
#### 1. Set card reviewed
`https://www.lingq.com/api/v2/{languageCode}/cards/{primaryKey}/review/`

Tells lingq that the card has been reviewed via srs on the date this is sent. Will update lingqs srs_due_date. 

It seems like this needs to be called instead of changing the due date manually with the patch url.

This doesn't need anything in it's body, but some testing should be done to see if an srs_due_date or status_changed_date can be supplied. 

Returns an object showing the new srs_due_date and status_changed_date:
```
{
    "srs_due_date": date,
    "status_changed_date": date
}
```