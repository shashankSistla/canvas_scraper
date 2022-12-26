# Canvas Lecture Scraper
##### _Currently only supports UCSD Canvas_

The scraper provides a simple CLI interface to download all media gallery contents of a particular course. 
## Installations required

In order for the web scraper to run, you will need the following python libraries installed.
- selenium
- colorama 
- youtube_dl

To scraper will place lectures of a particular course in the same folder in the directory of the scraper itself. 

To run the scraper, simply open up a command prompt/terminal, and run

```sh
python scraper.py
```
1) You will have to enter your SSO credentials
2) Enter the course code
2) It will automatically send a push notification to the duo app on your phone. Press approve.
3) Kick back and relax while the videos download


## But what is my course code?
To find your course code, log in to canvas and navigate to any course. The URL should look like this:
`https://canvas.ucsd.edu/courses/39545`
The number after the `courses/` is the course code. 

## Todo
1. Add a selection option in the CLI, instead of having to find the course code before hand
2. Add error handling. Right now, wrong passwords and incorrect course codes are not handled.
3. Progress bars for video downloads are not working on Windows Command Prompy.

## License

MIT



