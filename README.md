
# Instagram Image Downloader (CLI Version)

## Overview
This program is a command-line tool for downloading images from an Instagram account using valid session cookies. It leverages the `instaloader` library to interact with Instagram and provides a simple guided process for selecting a cookie file, specifying a username, and choosing the number of images to download.

## Features
- Supports both `.json` and `.txt` cookie file formats.
- Automatically extracts the `sessionid` from cookies.
- Downloads a specified number of recent images from a public or accessible private Instagram account.
- Uses `tqdm` to display download progress.
- Saves images in a directory named after the Instagram username.

## Requirements
- Python 3.7 or later
- The following Python packages:
  - `instaloader`
  - `requests`
  - `tqdm`

## Installation
1. Clone or download this repository.
2. Install the required packages:
```bash
   pip install instaloader requests tqdm
````

## Usage

1. Run the program:

```bash
   python execute.py
 ```
1. Select a cookie file when prompted.
2. Enter the target Instagram username.
3. Specify the number of images to download.
4. The program will create a folder with the username and download the images there.

## Cookie File Guidelines

* The cookie file must contain a valid `sessionid` for an authenticated Instagram session.
* Supported formats:

  * **JSON**: Can be a dictionary containing a `"cookies"` list or a list of cookie dictionaries.
  * **TXT**: Must contain a `sessionid` entry.

## Notes

* The account associated with the cookie file must have permission to view the target profile (for private accounts).
* Avoid sharing your cookie file to protect your account security.

## License

This project is provided "as is" without warranty of any kind. Use at your own risk.


