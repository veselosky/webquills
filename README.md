# WebQuills.com

This is the code that runs (or one day will run) webquills.com.

## Design and things to do

[ ] Add django-distill for static site generation

### Base template and reusable components

[x] Break out *Masthead* include (example only)
[x] Break out *Nav menu* include (example only)
[x] Break out *CTA Jumbotron* include (example only)
[x] Break out *Featured posts* include (example only)
[ ] Break out *Article list* include (example only)
[x] Default title
[x] Default meta description
[ ] *Masthead* component implementation
[ ] *Nav menu* component implementation
[ ] *Article list* component implementation
[ ] OpenGraph metadata component
[x] Set default RichText features to: bold, italic, link, document-link, ol, ul, code,
    superscript, subscript, strikethrough
[x] HeadingBlock (with auto-anchor)
[ ] ImageBlock (with auto-attribution)
[x] EmbedBlock (for oEmbeds)
[ ] HRBlock (lol)
[ ] BlockquoteBlock (with citation)
[ ] CodeBlock

### Home Page

[ ] CTA Jumbotron block

### Category Page

[x] Add intro (StreamField) to Category model
[x] Add featured image to Category model
[ ] Add featured articles (M2M) to Category model

### Article Page

[x] Add body (StreamField) to Article model
[x] Add featured image to Article model
[x] Add attribution to Article model

Do I even want a sidebar? If yes, what should I put in it?
About the Author
Author links
Related Links
Affiliate Book Link
