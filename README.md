# Google Tools for Open WebUI

This tool provides functionalities to interact with Google Calendar and Gmail using the Google API within the [Open WebUI](https://github.com/open-webui/open-webui) platform. It allows you to fetch upcoming events from your calendar and retrieve emails from your inbox.

## Table of Contents
- [Get Started](#get-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

## Get Started

1. Follow the steps on the [Google API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) to obtain your credentials file.
2. Copy the contents of `google_tools.py` into your Open WebUI tools page (Workspace > Tools).

## Configuration

The following configuration values can be set under the `Valve` class:

- **`path_to_credentials`**: The absolute path to the `credentials.json` file. *Required!*
- **`default_calendar_entries`** (optional): The default number of calendar entries to fetch (default: 10).
- **`default_email_entries`** (optional): The default number of email entries to fetch (default: 10).

## Usage

- Enable the "Google Tools" tool for your model.
- Ask about upcoming events using the command `What are the upcoming events?`.
- Ask about noteworthy or actionable emails with the command `Are there any noteworthy or actionable emails?`.

**Note:** When running the query for the first time, you'll be prompted to authenticate and authorize the application to access your Google account through a Google OAuth dialog.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.