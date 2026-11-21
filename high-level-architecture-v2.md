# P-article
#### Dictionary
- article - scientific article from science magazine, in pdf format
- article_id - identifier of the article, UUIDv4
- particle - processed part of the article, in md format, images saved as png are linked but stored separately. Can be identified by using article_id and part_no
- header - generated catchy header for particle, multiple headers exist for one particle
- panel_image - image generated for a panel, separate from the images taken from the article
- metadata - article metadata, authors, affiliations, title, topic, number of particles generated from the article
- panel - mobile application concept of displaying particle on main page, consists of header and panel_image
***
## Assumptions
### Server assumptions
Server is stateless (it keeps no client session state) and serves processed articles through a REST API. There is no concurrency needed (each server is dedicated to one user). There wouldn't be many articles - max 1000 per user when 100 is more probable.
Articles are input to the server through a server-side interface (not through the API), processed there and stored as files.
Processed data (particles, headers, images) never changes after it is generated.
Panel images are 600x400 px. Article images are extracted from the pdf, there are only a few of them per particle.
Authorization is skipped.
### Client assumption
Client is an Android mobile app.
Mobile app stores user data and state: history of read articles, which particles were seen and which were marked to not be shown again. It's responsible for caching particles not-yet-read by user, so offline usage is allowed.
Client learns about new articles by fetching the article list and comparing it with its cache.
Particles are displayed on mobile app as in social media platform - firstly the panels are shown to the user. After interacting with it the whole particle is presented. Client chooses which panel of a particle is shown (probably in random order).
***
## Communication
All communication is initiated by client. Following endpoints are used:
- GET `/articles` - returns ids of all articles available on server with number of particles in each
- GET `/articles/{article_id}` - returns metadata of the article
- GET `/articles/{article_id}/particles/{part_no}/panels` - returns list of panels (header and panel_image pairs)
- GET `/articles/{article_id}/particles/{part_no}` - returns particle - text and relevant images
- POST `/recommendations` - in request body are sent previously read articles, server returns list of article ids recommended

Images are sent inside the JSON responses, encoded in base64.

#### Examples
`GET /articles`
```json
[
  { "id": "3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71", "particle_count": 7 },
  { "id": "9c7e1a2d-5b3f-4c8e-a6d0-1f4b7e9c2a35", "particle_count": 4 }
]
```

`GET /articles/3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71`
```json
{
  "id": "3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71",
  "title": "...",
  "authors": ["..."],
  "affiliations": ["..."],
  "topic": "...",
  "particle_count": 7
}
```

`GET /articles/3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71/particles/1/panels`
```json
[
  { "header": "Catchy header A", "image": "<base64 png>" },
  { "header": "Catchy header B", "image": "<base64 png>" }
]
```

`GET /articles/3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71/particles/1`
```json
{
  "content": "... ![](fig1.png) ...",
  "images": { "fig1.png": "<base64 png>" }
}
```
Images in `content` are referenced by names that are keys of `images` in the same response.

`POST /recommendations`
```json
// request
{ "read_article_ids": ["3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71", "b81d4e6a-2c9f-4a3b-8e5d-7f0a1c6b9d24"] }
// response
{ "article_ids": ["9c7e1a2d-5b3f-4c8e-a6d0-1f4b7e9c2a35", "e4a9c2f7-1b6d-4f8a-b3e0-5d2c7a9f1e86"] }
```

Errors are returned as `application/problem+json` (RFC 9457):
```json
{ "status": 404, "title": "Not Found", "detail": "Article 0b6e2f9a-4d1c-4b7e-9f3a-8c5d2e7b1a40 does not exist" }
```
***
## Storage
Data is kept in folders on disk:
```
data/
  panel_images/
    <name>.png
  articles/
    <article_id>/
      images/                         # images extracted from the pdf
      parts/                          # original parts of the article
      particles/                      # parts enhanced by LLM
      metadata.json
      panels.json                     # header and path to image from panel_images, keyed by part_no
      original_article.pdf            # for debugging purposes
```

`panels.json`:
```json
{
  "1": [
    { "header": "Catchy header A", "image": "panel_images/ship-storm.png" },
    { "header": "Catchy header B", "image": "panel_images/fuel-gauge.png" }
  ],
  "2": [ ... ]
}
```
***
## Architecture decisions
### Read-only API
Articles are input to the server through a server-side interface, so the client never uploads or deletes them. The API exposes only reading, plus computing recommendations.

### Article list separate from metadata
Client fetches the article list to learn about new articles, so the list should be small - it contains only ids and number of particles. The number of particles is needed to know which `part_no` can be fetched without an extra request.
Metadata (authors, affiliations, ...) is fetched with `GET /articles/{article_id}` only for selected articles. Processed data never changes, so the client caches it and never fetches it again.

### Panels are served by the server
A panel is a header paired with a panel_image generated for it. The panel_image is separate data, not taken from the article, so the client can't build a panel from the particle and needs its own endpoint.

### Images sent together with panels and particles
An image has no meaning without its panel or particle. The client caches not-yet-read particles for offline usage, so it always needs the text and images at the same time. One request per particle means it is either cached completely or not at all - there is no case where the text is offline but the images are missing. Processed data never changes, so cached particles never need to be refreshed.
Separate image URLs would help with HTTP caching and lazy loading, but with one user per server and particles downloaded as a whole these don't matter.
Base64 in JSON is used because it's easy to parse on Android (`JSONObject`). The overhead is acceptable for 400x600 px panel images and a few article images per particle. Zip and `multipart/related` were rejected as harder to handle on the client.

### Recommendations sent with POST
Recommendations only read data, but POST is used because the other methods are hard to handle:
- GET with read article ids in the query - with up to 1000 articles the URL could exceed length limits,
- QUERY - semantically the best fit (safe and idempotent), but it's a new method that `HttpURLConnection` used by the app does not support.

### No versioning and no pagination
Each server is dedicated to one user and talks to one client, and there are at most 1000 articles. API versioning and pagination would add complexity without any benefit.
